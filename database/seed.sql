INSERT INTO Artists (name) VALUES
    ('The Beatles'),
    ('Led Zeppelin'),
    ('Pink Floyd'),
    ('Queen')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Genres (name) VALUES
    ('Rock'),
    ('Classic Rock'),
    ('Progressive Rock'),
    ('Psychedelic Rock')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Albums (title, artist_id)
SELECT album.title, artist.artist_id
FROM (
    VALUES
        ('Abbey Road', 'The Beatles'),
        ('The White Album', 'The Beatles'),
        ('Led Zeppelin IV', 'Led Zeppelin'),
        ('The Dark Side of the Moon', 'Pink Floyd'),
        ('A Night at the Opera', 'Queen')
) AS album(title, artist_name)
JOIN Artists AS artist ON artist.name = album.artist_name
ON CONFLICT (title, artist_id) DO NOTHING;

INSERT INTO Songs (title, artist_id, album_id)
SELECT track.title, artist.artist_id, album.album_id
FROM (
    VALUES
        ('Come Together', 'The Beatles', 'Abbey Road'),
        ('Something', 'The Beatles', 'Abbey Road'),
        ('While My Guitar Gently Weeps', 'The Beatles', 'The White Album'),
        ('Black Dog', 'Led Zeppelin', 'Led Zeppelin IV'),
        ('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV'),
        ('Money', 'Pink Floyd', 'The Dark Side of the Moon'),
        ('Bohemian Rhapsody', 'Queen', 'A Night at the Opera'),
        ('Love of My Life', 'Queen', 'A Night at the Opera')
) AS track(title, artist_name, album_title)
JOIN Artists AS artist ON artist.name = track.artist_name
JOIN Albums AS album
    ON album.title = track.album_title
    AND album.artist_id = artist.artist_id
WHERE NOT EXISTS (
    SELECT 1
    FROM Songs AS song
    WHERE song.title = track.title
      AND song.artist_id = artist.artist_id
);

INSERT INTO SongGenre (song_id, genre_id)
SELECT song.song_id, genre.genre_id
FROM Songs AS song
JOIN Artists AS artist ON artist.artist_id = song.artist_id
JOIN Genres AS genre ON genre.name = CASE song.title
    WHEN 'While My Guitar Gently Weeps' THEN 'Psychedelic Rock'
    WHEN 'Stairway to Heaven' THEN 'Classic Rock'
    WHEN 'Money' THEN 'Progressive Rock'
    WHEN 'Bohemian Rhapsody' THEN 'Classic Rock'
    WHEN 'Love of My Life' THEN 'Rock'
    ELSE 'Rock'
END
WHERE artist.name IN ('The Beatles', 'Led Zeppelin', 'Pink Floyd', 'Queen')
ON CONFLICT (song_id) DO NOTHING;
