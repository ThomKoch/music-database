import os
import unittest
from pathlib import Path

try:
    import psycopg2
except ImportError:
    psycopg2 = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_DSN = os.getenv("TEST_DATABASE_DSN")


@unittest.skipUnless(
    psycopg2 is not None and TEST_DATABASE_DSN,
    "TEST_DATABASE_DSN is not configured",
)
class DatabaseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = psycopg2.connect(TEST_DATABASE_DSN)
        cls.connection.autocommit = True
        schema = (PROJECT_ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
        with cls.connection.cursor() as cursor:
            cursor.execute(schema)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE Users, Artists, Genres RESTART IDENTITY CASCADE"
            )

    def create_catalog_entries(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Artists (name) VALUES ('Test Artist') RETURNING artist_id"
            )
            artist_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO Albums (title, artist_id) VALUES ('Test Album', %s) RETURNING album_id",
                (artist_id,),
            )
            album_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO Songs (title, artist_id, album_id) VALUES ('Test Song', %s, %s) RETURNING song_id",
                (artist_id, album_id),
            )
            song_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO Genres (name) VALUES ('Test Genre') RETURNING genre_id"
            )
            genre_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO SongGenre (song_id, genre_id) VALUES (%s, %s)",
                (song_id, genre_id),
            )
        return artist_id, album_id, song_id

    def create_user_and_playlist(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Users (username, email, password_hash)
                VALUES ('test-user', 'test@example.com', 'hash')
                RETURNING user_id
                """
            )
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO Playlists (name, user_id) VALUES ('Test Playlist', %s) RETURNING playlist_id",
                (user_id,),
            )
            return cursor.fetchone()[0]

    def test_song_relations_are_removed_with_song(self):
        _, _, song_id = self.create_catalog_entries()
        playlist_id = self.create_user_and_playlist()

        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO PlaylistSongs (playlist_id, song_id) VALUES (%s, %s)",
                (playlist_id, song_id),
            )
            cursor.execute("DELETE FROM Songs WHERE song_id = %s", (song_id,))
            cursor.execute(
                "SELECT COUNT(*) FROM SongGenre WHERE song_id = %s", (song_id,)
            )
            self.assertEqual(cursor.fetchone()[0], 0)
            cursor.execute(
                "SELECT COUNT(*) FROM PlaylistSongs WHERE song_id = %s", (song_id,)
            )
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_deleting_artist_cascades_to_catalog(self):
        artist_id, album_id, _ = self.create_catalog_entries()

        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM Artists WHERE artist_id = %s", (artist_id,))
            cursor.execute(
                "SELECT COUNT(*) FROM Albums WHERE album_id = %s", (album_id,)
            )
            self.assertEqual(cursor.fetchone()[0], 0)
            cursor.execute(
                "SELECT COUNT(*) FROM Songs WHERE artist_id = %s", (artist_id,)
            )
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_playlist_timestamp_changes_when_song_is_removed(self):
        _, _, song_id = self.create_catalog_entries()
        playlist_id = self.create_user_and_playlist()

        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO PlaylistSongs (playlist_id, song_id) VALUES (%s, %s)",
                (playlist_id, song_id),
            )
            cursor.execute(
                "UPDATE Playlists SET last_modified = TIMESTAMP '2000-01-01' WHERE playlist_id = %s",
                (playlist_id,),
            )
            cursor.execute(
                "DELETE FROM PlaylistSongs WHERE playlist_id = %s AND song_id = %s",
                (playlist_id, song_id),
            )
            cursor.execute(
                "SELECT last_modified FROM Playlists WHERE playlist_id = %s",
                (playlist_id,),
            )
            self.assertGreater(cursor.fetchone()[0].year, 2000)


if __name__ == "__main__":
    unittest.main()
