CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(129) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    admin_status BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Artists (
    artist_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Albums (
    album_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES Artists(artist_id) ON DELETE CASCADE,
    UNIQUE (title, artist_id)
);

CREATE TABLE IF NOT EXISTS Songs (
    song_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES Artists(artist_id) ON DELETE CASCADE,
    album_id INTEGER REFERENCES Albums(album_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Playlists (
    playlist_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    last_modified TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS PlaylistSongs (
    playlist_id INTEGER NOT NULL REFERENCES Playlists(playlist_id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES Songs(song_id) ON DELETE CASCADE,
    PRIMARY KEY (playlist_id, song_id)
);

CREATE TABLE IF NOT EXISTS Genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS SongGenre (
    song_id INTEGER PRIMARY KEY REFERENCES Songs(song_id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES Genres(genre_id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION update_playlist_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE Playlists
        SET last_modified = NOW()
        WHERE playlist_id = OLD.playlist_id;
        RETURN OLD;
    END IF;

    UPDATE Playlists
    SET last_modified = NOW()
    WHERE playlist_id = NEW.playlist_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_playlist_last_modified ON PlaylistSongs;

CREATE TRIGGER update_playlist_last_modified
AFTER INSERT OR UPDATE OR DELETE ON PlaylistSongs
FOR EACH ROW
EXECUTE FUNCTION update_playlist_last_modified();
