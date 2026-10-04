from tkinter import END, FALSE, Listbox, Tk, Toplevel, messagebox, simpledialog, ttk

import bcrypt
import psycopg2

from music_database.config import DatabaseSettings
from music_database.validation import is_valid_email

conn = None
cursor = None
main = None
current_user_id = None
screen_width = 0
screen_height = 0


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(stored_password, provided_password):
    return bcrypt.checkpw(
        provided_password.encode("utf-8"), stored_password.encode("utf-8")
    )


def insert_user():
    username = entry_username.get()
    email = entry_email.get()
    password = entry_password.get()

    if username and email and password:
        if is_valid_email(email):
            password_hash = hash_password(password)
            try:
                cursor.execute(
                    "INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, password_hash),
                )
                conn.commit()
                messagebox.showinfo("Erfolg", "Benutzer erfolgreich hinzugefügt")
                clear_user_entries()
            except psycopg2.Error as error:
                conn.rollback()
                messagebox.showerror(
                    "Fehler",
                    f"Benutzer konnte nicht erstellt werden: {error.diag.message_primary or str(error)}",
                )
        else:
            messagebox.showwarning("Warnung", "Bitte eine gültige E-Mail angeben")
    else:
        messagebox.showwarning("Warnung", "Bitte alle Felder ausfüllen")


def clear_user_entries():
    entry_username.delete(0, END)
    entry_email.delete(0, END)
    entry_password.delete(0, END)


def login_user():
    global current_user_id
    username = entry_login_username.get()
    password = entry_login_password.get()

    if username and password:
        cursor.execute(
            "SELECT user_id, password_hash FROM Users WHERE username = %s OR email = %s",
            (username, username),
        )
        user_data = cursor.fetchone()
        if user_data and check_password(user_data[1], password):
            messagebox.showinfo("Login", "Login erfolgreich")
            current_user_id = user_data[0]
            show_user_interface()
        else:
            messagebox.showwarning("Error", "Falsche Login-Daten")
    else:
        messagebox.showwarning("Error", "Bitte alle Felder ausfüllen")


def show_user_interface():
    for widget in main.winfo_children():
        widget.grid_forget()

    window_width_user_interface = 238
    window_height_user_interface = 100

    x_position_user_interface = int(
        (screen_width / 2) - (window_width_user_interface / 2)
    )
    y_position_user_interface = int(
        (screen_height / 2) - (window_height_user_interface / 2)
    )

    main.geometry(
        f"{window_width_user_interface}x{window_height_user_interface}+{x_position_user_interface}+{y_position_user_interface}"
    )

    style_button = ttk.Style()
    style_button.configure("Start.TButton", font=("Arial", 14, "bold"))

    button_view_playlists = ttk.Button(
        main,
        text="Meine Playlists anzeigen",
        command=view_playlists,
        style="Start.TButton",
    )
    button_view_playlists.grid(row=1, column=0)

    button_search = ttk.Button(
        main, text="Suchen", command=search, style="Start.TButton"
    )
    button_search.grid(row=2, column=0)

    button_admin_menu = ttk.Button(
        main, text="Admin-Menü", command=admin_menu, style="Start.TButton"
    )
    button_admin_menu.grid(row=3, column=0)


def admin_menu():
    cursor.execute(
        "SELECT admin_status FROM Users WHERE user_id = %s", (current_user_id,)
    )
    result = cursor.fetchone()
    admin_status = result[0]
    if admin_status is True:
        show_admin_menu()
    else:
        messagebox.showinfo(
            "Keine Berechtigung",
            "Du hast keine Berechtigungen, neue Einträge zu erstellen",
        )


def show_admin_menu():
    admin_window = Toplevel(main)
    admin_window.title("Admin-Menü")

    window_width_admin = 721
    window_height_admin = 65

    x_position_admin = int((screen_width / 2) - (window_width_admin / 2))
    y_position_admin = int((screen_height / 2) - (window_height_admin / 2))

    admin_window.geometry(
        f"{window_width_admin}x{window_height_admin}+{x_position_admin}+{y_position_admin}"
    )
    admin_window.resizable(FALSE, FALSE)

    style_button = ttk.Style()
    style_button.configure("Start.TButton", font=("Arial", 14, "bold"))

    button_add_song = ttk.Button(
        admin_window,
        text="Song hinzufügen",
        command=add_song_menu,
        style="Start.TButton",
    )
    button_add_song.grid(row=1, column=0)

    button_add_artist = ttk.Button(
        admin_window,
        text="Künstler hinzufügen",
        command=add_artist_menu,
        style="Start.TButton",
    )
    button_add_artist.grid(row=1, column=1)

    button_add_album = ttk.Button(
        admin_window,
        text="Album hinzufügen",
        command=add_album_menu,
        style="Start.TButton",
    )
    button_add_album.grid(row=1, column=2)

    button_add_genre = ttk.Button(
        admin_window,
        text="Genre hinzufügen",
        command=add_genre_menu,
        style="Start.TButton",
    )
    button_add_genre.grid(row=1, column=3)

    button_remove_song = ttk.Button(
        admin_window,
        text="Song entfernen",
        command=remove_song_menu,
        style="Start.TButton",
    )
    button_remove_song.grid(row=2, column=0)

    button_remove_artist = ttk.Button(
        admin_window,
        text="Künstler entfernen",
        command=remove_artist_menu,
        style="Start.TButton",
    )
    button_remove_artist.grid(row=2, column=1)

    button_remove_album = ttk.Button(
        admin_window,
        text="Album entfernen",
        command=remove_album_menu,
        style="Start.TButton",
    )
    button_remove_album.grid(row=2, column=2)

    button_remove_genre = ttk.Button(
        admin_window,
        text="Genre entfernen",
        command=remove_genre_menu,
        style="Start.TButton",
    )
    button_remove_genre.grid(row=2, column=3)


def add_song_menu():
    add_song_window = Toplevel(main)
    add_song_window.title("Song hinzufügen")

    window_width_add_song = 200
    window_height_add_song = 150

    x_position_add_song = int((screen_width / 2) - (window_width_add_song / 2))
    y_position_add_song = int((screen_height / 2) - (window_height_add_song / 2))

    add_song_window.geometry(
        f"{window_width_add_song}x{window_height_add_song}+{x_position_add_song}+{y_position_add_song}"
    )
    add_song_window.resizable(FALSE, FALSE)

    label_title = ttk.Label(add_song_window, text="Songtitel:")
    label_title.grid(row=0, column=0, pady=5, padx=3)
    entry_title = ttk.Entry(add_song_window)
    entry_title.grid(row=0, column=1, pady=5)

    label_genre = ttk.Label(add_song_window, text="Genre:")
    label_genre.grid(row=1, column=0, pady=5, padx=3)
    entry_genre = ttk.Entry(add_song_window)
    entry_genre.grid(row=1, column=1, pady=5)

    label_artist = ttk.Label(add_song_window, text="Künstler:")
    label_artist.grid(row=2, column=0, pady=5, padx=3)
    entry_artist = ttk.Entry(add_song_window)
    entry_artist.grid(row=2, column=1, pady=5)

    label_album = ttk.Label(add_song_window, text="Album:")
    label_album.grid(row=3, column=0, pady=5, padx=3)
    entry_album = ttk.Entry(add_song_window)
    entry_album.grid(row=3, column=1, pady=5)

    button_submit = ttk.Button(
        add_song_window,
        text="Song hinzufügen",
        command=lambda: add_song(
            add_song_window,
            entry_title.get(),
            entry_artist.get(),
            entry_album.get(),
            entry_genre.get(),
        ),
    )
    button_submit.grid(row=4, column=1)


def add_song(add_song_window, title, artist, album, genre):
    if not title or not artist or not genre:
        messagebox.showerror(
            "Fehler", "Titel, Künstler und Genre müssen ausgefüllt werden."
        )
        return

    try:
        cursor.execute("BEGIN")
        cursor.execute("SELECT artist_id FROM Artists WHERE name = %s", (artist,))
        artist_result = cursor.fetchone()
        if artist_result is None:
            raise ValueError(f"Künstler '{artist}' existiert nicht.")
        artist_id = artist_result[0]
        cursor.execute("SELECT genre_id FROM Genres WHERE name = %s", (genre,))
        genre_result = cursor.fetchone()
        if genre_result is None:
            raise ValueError(f"Genre '{genre}' existiert nicht.")
        genre_id = genre_result[0]
        if album:
            cursor.execute(
                "SELECT album_id FROM Albums WHERE artist_id = %s AND title = %s",
                (artist_id, album),
            )
            album_result = cursor.fetchone()
            if album_result is None:
                raise ValueError(
                    f"Album '{album}' für Künstler '{artist}' existiert nicht."
                )
            album_id = album_result[0]
            cursor.execute(
                """
                INSERT INTO Songs (title, artist_id, album_id)
                VALUES (%s, %s, %s) RETURNING song_id
                """,
                (title, artist_id, album_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Songs (title, artist_id)
                VALUES (%s, %s) RETURNING song_id
                """,
                (title, artist_id),
            )

        song_id_result = cursor.fetchone()
        song_id = song_id_result[0]
        cursor.execute(
            "INSERT INTO SongGenre (song_id, genre_id) VALUES (%s, %s)",
            (song_id, genre_id),
        )
        conn.commit()
        add_song_window.destroy()
        messagebox.showinfo("Erfolg", "Song hinzugefügt")
    except (psycopg2.Error, ValueError) as e:
        conn.rollback()
        messagebox.showerror("Fehler", f"Song konnte nicht hinzugefügt werden: {e!s}")


def add_artist_menu():
    add_artist_window = Toplevel(main)
    add_artist_window.title("Künstler hinzufügen")

    window_width_add_artist = 200
    window_height_add_artist = 65

    x_position_add_artist = int((screen_width / 2) - (window_width_add_artist / 2))
    y_position_add_artist = int((screen_height / 2) - (window_height_add_artist / 2))

    add_artist_window.geometry(
        f"{window_width_add_artist}x{window_height_add_artist}+{x_position_add_artist}+{y_position_add_artist}"
    )
    add_artist_window.resizable(FALSE, FALSE)

    label_name = ttk.Label(add_artist_window, text="Name:")
    label_name.grid(row=0, column=0, pady=5, padx=3)
    entry_name = ttk.Entry(add_artist_window)
    entry_name.grid(row=0, column=1, pady=5)

    button_submit = ttk.Button(
        add_artist_window,
        text="Künstler hinzufügen",
        command=lambda: add_artist(add_artist_window, entry_name.get()),
    )
    button_submit.grid(row=1, column=1)


def add_artist(add_artist_window, name):
    if name:
        try:
            cursor.execute("INSERT INTO Artists (name) VALUES (%s)", (name,))
            conn.commit()
            add_artist_window.destroy()
            messagebox.showinfo("Erfolg", "Künstler hinzugefügt")
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Künstler konnte nicht hinzugefügt werden: {error.diag.message_primary or str(error)}",
            )


def add_album_menu():
    add_album_window = Toplevel(main)
    add_album_window.title("Album hinzufügen")

    window_width_add_album = 200
    window_height_add_album = 95

    x_position_add_album = int((screen_width / 2) - (window_width_add_album / 2))
    y_position_add_album = int((screen_height / 2) - (window_height_add_album / 2))

    add_album_window.geometry(
        f"{window_width_add_album}x{window_height_add_album}+{x_position_add_album}+{y_position_add_album}"
    )
    add_album_window.resizable(FALSE, FALSE)

    label_name = ttk.Label(add_album_window, text="Name:")
    label_name.grid(row=0, column=0, pady=5, padx=3)
    entry_name = ttk.Entry(add_album_window)
    entry_name.grid(row=0, column=1, pady=5)

    label_artist = ttk.Label(add_album_window, text="Künstler:")
    label_artist.grid(row=1, column=0, pady=5, padx=3)
    entry_artist = ttk.Entry(add_album_window)
    entry_artist.grid(row=1, column=1, pady=5)

    button_submit = ttk.Button(
        add_album_window,
        text="Album hinzufügen",
        command=lambda: add_album(
            add_album_window, entry_name.get(), entry_artist.get()
        ),
    )
    button_submit.grid(row=2, column=1)


def add_album(add_artist_window, name, artist):
    if name and artist:
        try:
            cursor.execute(
                "INSERT INTO Albums (title, artist_id) VALUES (%s, (SELECT artist_id FROM Artists WHERE name = %s))",
                (name, artist),
            )
            conn.commit()
            add_artist_window.destroy()
            messagebox.showinfo("Erfolg", "Album hinzugefügt")
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Album konnte nicht hinzugefügt werden: {error.diag.message_primary or str(error)}",
            )


def add_genre_menu():
    add_genre_window = Toplevel(main)
    add_genre_window.title("Genre hinzufügen")

    window_width_add_genre = 200
    window_height_add_genre = 65

    x_position_add_genre = int((screen_width / 2) - (window_width_add_genre / 2))
    y_position_add_genre = int((screen_height / 2) - (window_height_add_genre / 2))

    add_genre_window.geometry(
        f"{window_width_add_genre}x{window_height_add_genre}+{x_position_add_genre}+{y_position_add_genre}"
    )
    add_genre_window.resizable(FALSE, FALSE)

    label_name = ttk.Label(add_genre_window, text="Name:")
    label_name.grid(row=0, column=0, pady=5, padx=3)
    entry_name = ttk.Entry(add_genre_window)
    entry_name.grid(row=0, column=1, pady=5)

    button_submit = ttk.Button(
        add_genre_window,
        text="Genre hinzufügen",
        command=lambda: add_genre(add_genre_window, entry_name.get()),
    )
    button_submit.grid(row=2, column=1)


def add_genre(add_genre_window, name):
    if name:
        try:
            cursor.execute("INSERT INTO Genres (name) VALUES (%s)", (name,))
            conn.commit()
            add_genre_window.destroy()
            messagebox.showinfo("Erfolg", "Genre hinzugefügt")
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Genre konnte nicht hinzugefügt werden: {error.diag.message_primary or str(error)}",
            )


def remove_song_menu():
    remove_song_window = Toplevel(main)
    remove_song_window.title("Song entfernen")

    window_width_remove_song = 300
    window_height_remove_song = 250

    x_position_remove_song = int((screen_width / 2) - (window_width_remove_song / 2))
    y_position_remove_song = int((screen_height / 2) - (window_height_remove_song / 2))

    remove_song_window.geometry(
        f"{window_width_remove_song}x{window_height_remove_song}+{x_position_remove_song}+{y_position_remove_song}"
    )
    remove_song_window.resizable(FALSE, FALSE)

    cursor.execute("SELECT song_id, title FROM Songs")
    songs = cursor.fetchall()

    listbox_songs = Listbox(remove_song_window, width=40, height=10)
    listbox_songs.pack(pady=20)

    for song in songs:
        listbox_songs.insert(END, song[1])

    button_remove_song = ttk.Button(
        remove_song_window,
        text="Song entfernen",
        command=lambda: remove_song(listbox_songs),
    )
    button_remove_song.pack()


def remove_song(listbox_songs):
    cursor.execute("SELECT song_id, title FROM Songs")
    songs = cursor.fetchall()
    selection = listbox_songs.curselection()
    if selection:
        index = selection[0]
        song_id = songs[index][0]
        try:
            cursor.execute("DELETE FROM Songs WHERE song_id = %s", (song_id,))
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Song konnte nicht entfernt werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute("SELECT song_id, title FROM Songs")
        songs = cursor.fetchall()
        listbox_songs.delete(0, END)
        for song in songs:
            listbox_songs.insert(END, song[1])


def remove_artist_menu():
    remove_artist_window = Toplevel(main)
    remove_artist_window.title("Künstler entfernen")

    window_width_remove_artist = 300
    window_height_remove_artist = 250

    x_position_remove_artist = int(
        (screen_width / 2) - (window_width_remove_artist / 2)
    )
    y_position_remove_artist = int(
        (screen_height / 2) - (window_height_remove_artist / 2)
    )

    remove_artist_window.geometry(
        f"{window_width_remove_artist}x{window_height_remove_artist}+{x_position_remove_artist}+{y_position_remove_artist}"
    )
    remove_artist_window.resizable(FALSE, FALSE)

    cursor.execute("SELECT artist_id, name FROM Artists")
    artists = cursor.fetchall()

    listbox_artists = Listbox(remove_artist_window, width=40, height=10)
    listbox_artists.pack(pady=20)

    for artist in artists:
        listbox_artists.insert(END, artist[1])

    button_remove_artist = ttk.Button(
        remove_artist_window,
        text="Künstler entfernen",
        command=lambda: remove_artist(listbox_artists),
    )
    button_remove_artist.pack()


def remove_artist(listbox_artists):
    cursor.execute("SELECT artist_id, name FROM Artists")
    artists = cursor.fetchall()
    selection = listbox_artists.curselection()
    if selection:
        index = selection[0]
        artist_id = artists[index][0]
        try:
            cursor.execute("DELETE FROM Artists WHERE artist_id = %s", (artist_id,))
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Künstler konnte nicht entfernt werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute("SELECT artist_id, name FROM Artists")
        artists = cursor.fetchall()
        listbox_artists.delete(0, END)
        for artist in artists:
            listbox_artists.insert(END, artist[1])


def remove_album_menu():
    remove_album_window = Toplevel(main)
    remove_album_window.title("Album entfernen")

    window_width_remove_album = 300
    window_height_remove_album = 250

    x_position_remove_album = int((screen_width / 2) - (window_width_remove_album / 2))
    y_position_remove_album = int(
        (screen_height / 2) - (window_height_remove_album / 2)
    )

    remove_album_window.geometry(
        f"{window_width_remove_album}x{window_height_remove_album}+{x_position_remove_album}+{y_position_remove_album}"
    )
    remove_album_window.resizable(FALSE, FALSE)

    cursor.execute("SELECT album_id, title FROM Albums")
    albums = cursor.fetchall()

    listbox_albums = Listbox(remove_album_window, width=40, height=10)
    listbox_albums.pack(pady=20)

    for album in albums:
        listbox_albums.insert(END, album[1])

    button_remove_album = ttk.Button(
        remove_album_window,
        text="Album entfernen",
        command=lambda: remove_album(listbox_albums),
    )
    button_remove_album.pack()


def remove_album(listbox_albums):
    cursor.execute("SELECT album_id, title FROM Albums")
    albums = cursor.fetchall()
    selection = listbox_albums.curselection()
    if selection:
        index = selection[0]
        album_id = albums[index][0]
        try:
            cursor.execute("DELETE FROM Albums WHERE album_id = %s", (album_id,))
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Album konnte nicht entfernt werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute("SELECT album_id, title FROM Albums")
        albums = cursor.fetchall()
        listbox_albums.delete(0, END)
        for album in albums:
            listbox_albums.insert(END, album[1])


def remove_genre_menu():
    remove_genre_window = Toplevel(main)
    remove_genre_window.title("Genre entfernen")

    window_width_remove_genre = 300
    window_height_remove_genre = 250

    x_position_remove_genre = int((screen_width / 2) - (window_width_remove_genre / 2))
    y_position_remove_genre = int(
        (screen_height / 2) - (window_height_remove_genre / 2)
    )

    remove_genre_window.geometry(
        f"{window_width_remove_genre}x{window_height_remove_genre}+{x_position_remove_genre}+{y_position_remove_genre}"
    )
    remove_genre_window.resizable(FALSE, FALSE)

    cursor.execute("SELECT genre_id, name FROM Genres")
    genres = cursor.fetchall()

    listbox_genres = Listbox(remove_genre_window, width=40, height=10)
    listbox_genres.pack(pady=20)

    for genre in genres:
        listbox_genres.insert(END, genre[1])

    button_remove_genre = ttk.Button(
        remove_genre_window,
        text="Genre entfernen",
        command=lambda: remove_genre(listbox_genres),
    )
    button_remove_genre.pack()


def remove_genre(listbox_genres):
    cursor.execute("SELECT genre_id, name FROM Genres")
    genres = cursor.fetchall()
    selection = listbox_genres.curselection()
    if selection:
        index = selection[0]
        genre_id = genres[index][0]
        try:
            cursor.execute("DELETE FROM Genres WHERE genre_id = %s", (genre_id,))
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Genre konnte nicht entfernt werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute("SELECT genre_id, name FROM Genres")
        genres = cursor.fetchall()
        listbox_genres.delete(0, END)
        for genre in genres:
            listbox_genres.insert(END, genre[1])


def view_playlists():
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()

    playlist_window = Toplevel(main)
    playlist_window.title("Meine Playlists")

    window_width_playlists = 400
    window_height_playlists = 300

    x_position_playlists = int((screen_width / 2) - (window_width_playlists / 2))
    y_position_playlists = int((screen_height / 2) - (window_height_playlists / 2))

    playlist_window.geometry(
        f"{window_width_playlists}x{window_height_playlists}+{x_position_playlists}+{y_position_playlists}"
    )
    playlist_window.resizable(FALSE, FALSE)

    listbox_playlists = Listbox(playlist_window, width=20, font="Helvetica 12")
    listbox_playlists.pack()

    for playlist in playlists:
        listbox_playlists.insert(END, playlist[1])

    button_open_playlist = ttk.Button(
        playlist_window,
        text="Playlist öffnen",
        command=lambda: show_playlist_songs(listbox_playlists),
    )
    button_open_playlist.pack()

    button_rename_playlist = ttk.Button(
        playlist_window,
        text="Playlist umbenennen",
        command=lambda: rename_playlist(listbox_playlists),
    )
    button_rename_playlist.pack()

    button_delete_playlist = ttk.Button(
        playlist_window,
        text="Playlist löschen",
        command=lambda: delete_playlist(listbox_playlists),
    )
    button_delete_playlist.pack()

    button_create_playlist = ttk.Button(
        playlist_window,
        text="Neue Playlist erstellen",
        command=lambda: create_new_playlist(listbox_playlists),
    )
    button_create_playlist.pack()


def show_playlist_songs(listbox_playlists):
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()
    selection = listbox_playlists.curselection()
    if selection:
        index = selection[0]
        playlist_id = playlists[index][0]

        cursor.execute(
            """
            SELECT Songs.song_id, Songs.title, Artists.name, Albums.title
            FROM Songs
            JOIN PlaylistSongs ON Songs.song_id = PlaylistSongs.song_id
            JOIN Artists ON Songs.artist_id = Artists.artist_id
            LEFT JOIN Albums ON Songs.album_id = Albums.album_id
            WHERE PlaylistSongs.playlist_id = %s
        """,
            (playlist_id,),
        )
        songs = cursor.fetchall()

        playlist_songs_window = Toplevel(main)
        playlist_songs_window.title("Playlist Songs")

        window_width_songs = 400
        window_height_songs = 300

        x_position_songs = int((screen_width / 2) - (window_width_songs / 2))
        y_position_songs = int((screen_height / 2) - (window_height_songs / 2))

        playlist_songs_window.geometry(
            f"{window_width_songs}x{window_height_songs}+{x_position_songs}+{y_position_songs}"
        )
        playlist_songs_window.resizable(FALSE, FALSE)

        listbox_songs = Listbox(playlist_songs_window, width=50)
        listbox_songs.pack()

        for song in songs:
            listbox_songs.insert(END, f"{song[1]}")

        listbox_songs.bind("<Button-3>", lambda event: on_right_click(event, songs))

        button_change_order = ttk.Button(
            playlist_songs_window, text="Song hinzufügen", command=lambda: search()
        )
        button_change_order.pack()

        button_remove_song = ttk.Button(
            playlist_songs_window,
            text="Song entfernen",
            command=lambda: remove_song_from_playlist(
                listbox_songs, playlist_id, songs
            ),
        )
        button_remove_song.pack()


def on_right_click(event, songs):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        song = songs[index]
        cursor.execute(
            "SELECT name FROM genres WHERE genre_id = (SELECT genre_id FROM SongGenre WHERE song_id = %s)",
            (song[0],),
        )
        genre_result = cursor.fetchone()
        genre = genre_result[0] if genre_result else "Unbekannt"
        album = song[3] or "Kein Album"
        messagebox.showinfo(
            "Song Details",
            f"Titel: {song[1]}\nGenre: {genre}\nKünstler: {song[2]}\nAlbum: {album}",
        )


def rename_playlist(listbox_playlists):
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()
    selection = listbox_playlists.curselection()
    if selection:
        index = selection[0]
        playlist_id = playlists[index][0]
        new_name = simpledialog.askstring(
            "Playlist umbenennen", "Neuer Name:", initialvalue=playlists[index][1]
        )
        if new_name:
            cursor.execute(
                "UPDATE Playlists SET name = %s WHERE playlist_id = %s",
                (new_name, playlist_id),
            )
            conn.commit()
            cursor.execute(
                "SELECT playlist_id, name FROM Playlists WHERE user_id = %s",
                (current_user_id,),
            )
            playlists = cursor.fetchall()
            listbox_playlists.delete(0, END)
            for playlist in playlists:
                listbox_playlists.insert(END, playlist[1])


def delete_playlist(listbox_playlists):
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()
    selection = listbox_playlists.curselection()
    if selection:
        index = selection[0]
        playlist_id = playlists[index][0]
        try:
            cursor.execute(
                "DELETE FROM Playlists WHERE playlist_id = %s", (playlist_id,)
            )
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Playlist konnte nicht gelöscht werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute(
            "SELECT playlist_id, name FROM Playlists WHERE user_id = %s",
            (current_user_id,),
        )
        playlists = cursor.fetchall()
        listbox_playlists.delete(0, END)
        for playlist in playlists:
            listbox_playlists.insert(END, playlist[1])


def remove_song_from_playlist(listbox_songs, playlist_id, songs):
    selection = listbox_songs.curselection()
    if selection:
        index = selection[0]
        song_id = songs[index][0]
        try:
            cursor.execute(
                "DELETE FROM PlaylistSongs WHERE playlist_id = %s AND song_id = %s",
                (playlist_id, song_id),
            )
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Song konnte nicht entfernt werden: {error.diag.message_primary or str(error)}",
            )
            return
        cursor.execute(
            """
            SELECT Songs.song_id, Songs.title, Artists.name, Albums.title
            FROM Songs
            JOIN PlaylistSongs ON Songs.song_id = PlaylistSongs.song_id
            JOIN Artists ON Songs.artist_id = Artists.artist_id
            LEFT JOIN Albums ON Songs.album_id = Albums.album_id
            WHERE PlaylistSongs.playlist_id = %s
        """,
            (playlist_id,),
        )
        songs[:] = cursor.fetchall()
        listbox_songs.delete(0, END)
        for song in songs:
            listbox_songs.insert(END, song[1])


def create_new_playlist(listbox_playlists):
    playlist_name = simpledialog.askstring("Playlist erstellen", "Name der Playlist:")

    if playlist_name:
        try:
            cursor.execute(
                "INSERT INTO Playlists (name, user_id) VALUES (%s, %s)",
                (playlist_name, current_user_id),
            )
            conn.commit()
            cursor.execute(
                "SELECT playlist_id, name FROM Playlists WHERE user_id = %s",
                (current_user_id,),
            )
            playlists = cursor.fetchall()
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Playlist konnte nicht erstellt werden: {error.diag.message_primary or str(error)}",
            )
            return

        listbox_playlists.delete(0, END)
        for playlist in playlists:
            listbox_playlists.insert(END, playlist[1])


def search():
    for window in main.winfo_children():
        if isinstance(window, Toplevel):
            window.destroy()

    search_window = Toplevel(main)
    search_window.title("Suchen")

    window_width_search = 300
    window_height_search = 100

    x_position_search = int((screen_width / 2) - (window_width_search / 2))
    y_position_search = int((screen_height / 2) - (window_height_search / 2))

    search_window.geometry(
        f"{window_width_search}x{window_height_search}+{x_position_search}+{y_position_search}"
    )
    search_window.resizable(FALSE, FALSE)

    label_search = ttk.Label(search_window, text="Suchbegriff:")
    label_search.pack()

    entry_search = ttk.Entry(search_window)
    entry_search.pack()

    button_search = ttk.Button(
        search_window, text="Suchen", command=lambda: perform_search(entry_search.get())
    )
    button_search.pack()


def perform_search(search_query):
    cursor.execute(
        """
        SELECT 'Song' as type, Songs.song_id as id, Songs.title as name, Artists.name as artist, Albums.title as album
        FROM Songs
        LEFT JOIN Artists ON Songs.artist_id = Artists.artist_id
        LEFT JOIN Albums ON Songs.album_id = Albums.album_id
        WHERE Songs.title ILIKE %s
        UNION
        SELECT 'Künstler' as type, Artists.artist_id as id, Artists.name as name, NULL as artist, NULL as album
        FROM Artists
        WHERE Artists.name ILIKE %s
        UNION
        SELECT 'Album' as type, Albums.album_id as id, Albums.title as name, Artists.name as artist, NULL as album
        FROM Albums
        JOIN Artists ON Albums.artist_id = Artists.artist_id
        WHERE Albums.title ILIKE %s
    """,
        (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"),
    )
    search_results = cursor.fetchall()

    search_results_window = Toplevel(main)
    if search_query:
        search_results_window.title(f"Suchergebnisse für '{search_query}'")
    else:
        search_results_window.title("Alle Einträge")

    window_width_search_results = 400
    window_height_search_results = 300

    x_position_search_results = int(
        (screen_width / 2) - (window_width_search_results / 2)
    )
    y_position_search_results = int(
        (screen_height / 2) - (window_height_search_results / 2)
    )

    search_results_window.geometry(
        f"{window_width_search_results}x{window_height_search_results}+{x_position_search_results}+{y_position_search_results}"
    )
    search_results_window.resizable(FALSE, FALSE)

    listbox_search_results = Listbox(search_results_window, width=50, height=15)
    listbox_search_results.pack(pady=20)

    for result in search_results:
        listbox_search_results.insert(END, f"{result[2]} ({result[0]})")

    listbox_search_results.bind(
        "<Button-3>", lambda event: on_search_right_click(event, search_results)
    )


def on_search_right_click(event, search_results):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        obj_type, obj_id, name, artist, album = search_results[index]
        if obj_type == "Song":
            cursor.execute(
                "SELECT name FROM genres WHERE genre_id = (SELECT genre_id FROM SongGenre WHERE song_id = %s)",
                (search_results[index][1],),
            )
            genre_result = cursor.fetchone()
            genre = genre_result[0] if genre_result else "Unbekannt"
            show_song_details(obj_id, name, artist, album, genre)
        elif obj_type == "Album":
            show_album_details(obj_id)
        elif obj_type == "Künstler":
            show_artist_details(obj_id)


def on_album_song_right_click(event, songs):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        cursor.execute(
            """
        SELECT Songs.song_id, Songs.title, Artists.name, Albums.title
        FROM Songs
        JOIN Artists ON Songs.artist_id = Artists.artist_id
        LEFT JOIN Albums ON Songs.album_id = Albums.album_id
        WHERE Songs.song_id = %s
    """,
            (songs[index][0],),
        )
        song = cursor.fetchall()
        if not song:
            messagebox.showwarning(
                "Hinweis", "Der ausgewählte Song ist nicht mehr vorhanden."
            )
            return
        song_id, title, artist, album = song[0]
        cursor.execute(
            "SELECT name FROM genres WHERE genre_id = (SELECT genre_id FROM SongGenre WHERE song_id = %s)",
            (song[0][0],),
        )
        genre_result = cursor.fetchone()
        genre = genre_result[0] if genre_result else "Unbekannt"
        show_song_details(song_id, title, artist, album, genre)


def on_album_right_click(event, albums):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        cursor.execute(
            """
            SELECT Songs.song_id, Songs.title, Artists.name
            FROM Songs
            JOIN Artists ON Songs.artist_id = Artists.artist_id
            WHERE Songs.album_id = %s
        """,
            (albums[index][0],),
        )
        songs = cursor.fetchall()
        cursor.execute(
            """
            SELECT Artists.name
            FROM Albums
            JOIN Artists ON Albums.artist_id = Artists.artist_id
            WHERE Albums.album_id = %s
        """,
            (albums[index][0],),
        )
        artist_result = cursor.fetchone()
        artist_name = artist_result[0] if artist_result else "Unbekannt"

        album_details_window = Toplevel(main)
        album_details_window.title("Album Details")

        window_width_album_details = 300
        window_height_album_details = 200

        x_position_album_details = int(
            (screen_width / 2) - (window_width_album_details / 2)
        )
        y_position_album_details = int(
            (screen_height / 2) - (window_height_album_details / 2)
        )

        album_details_window.geometry(
            f"{window_width_album_details}x{window_height_album_details}+{x_position_album_details}+{y_position_album_details}"
        )
        album_details_window.resizable(FALSE, FALSE)

        label_artist = ttk.Label(album_details_window, text=f"Künstler: {artist_name}")
        label_artist.pack(pady=5)
        listbox_album_songs = Listbox(album_details_window, width=30)
        listbox_album_songs.pack()

        for song in songs:
            listbox_album_songs.insert(END, song[1])

        listbox_album_songs.bind(
            "<Button-3>", lambda event: on_album_song_right_click(event, songs)
        )


def show_song_details(song_id, title, artist, album, genre):
    song_details_window = Toplevel(main)
    song_details_window.title("Songdetails")

    window_width_song_details = 300
    window_height_song_details = 200

    x_position_song_details = int((screen_width / 2) - (window_width_song_details / 2))
    y_position_song_details = int(
        (screen_height / 2) - (window_height_song_details / 2)
    )

    song_details_window.geometry(
        f"{window_width_song_details}x{window_height_song_details}+{x_position_song_details}+{y_position_song_details}"
    )
    song_details_window.resizable(FALSE, FALSE)

    label_title = ttk.Label(song_details_window, text=f"Titel: {title}")
    label_title.pack(pady=5)
    label_genre = ttk.Label(song_details_window, text=f"Genre: {genre}")
    label_genre.pack(pady=5)
    label_artist = ttk.Label(song_details_window, text=f"Künstler: {artist}")
    label_artist.pack(pady=5)
    label_album = ttk.Label(song_details_window, text=f"Album: {album or 'Kein Album'}")
    label_album.pack(pady=5)
    button_add_song = ttk.Button(
        song_details_window,
        text="Zur Playlist hinzufügen",
        command=lambda: add_song_to_playlist(song_details_window, song_id),
    )
    button_add_song.pack(pady=10)


def show_album_details(album_id):
    cursor.execute(
        """
        SELECT Songs.song_id, Songs.title, Artists.name
        FROM Songs
        JOIN Artists ON Songs.artist_id = Artists.artist_id
        WHERE Songs.album_id = %s
    """,
        (album_id,),
    )
    songs = cursor.fetchall()
    cursor.execute(
        """
        SELECT Artists.name
        FROM Albums
        JOIN Artists ON Albums.artist_id = Artists.artist_id
        WHERE Albums.album_id = %s
    """,
        (album_id,),
    )
    artist_result = cursor.fetchone()
    artist_name = artist_result[0] if artist_result else "Unbekannt"

    album_details_window = Toplevel(main)
    album_details_window.title("Album Details")

    window_width_album_details = 300
    window_height_album_details = 200

    x_position_album_details = int(
        (screen_width / 2) - (window_width_album_details / 2)
    )
    y_position_album_details = int(
        (screen_height / 2) - (window_height_album_details / 2)
    )

    album_details_window.geometry(
        f"{window_width_album_details}x{window_height_album_details}+{x_position_album_details}+{y_position_album_details}"
    )
    album_details_window.resizable(FALSE, FALSE)

    label_artist = ttk.Label(album_details_window, text=f"Künstler: {artist_name}")
    label_artist.pack(pady=5)
    listbox_album_songs = Listbox(album_details_window, width=30)
    listbox_album_songs.pack()

    for song in songs:
        listbox_album_songs.insert(END, song[1])

    listbox_album_songs.bind(
        "<Button-3>", lambda event: on_album_song_right_click(event, songs)
    )


def show_artist_details(artist_id):
    cursor.execute("SELECT name FROM Artists WHERE artist_id = %s", (artist_id,))
    artist_result = cursor.fetchone()
    if not artist_result:
        messagebox.showwarning(
            "Hinweis", "Der ausgewählte Künstler ist nicht mehr vorhanden."
        )
        return
    artist_name = artist_result[0]

    cursor.execute(
        """
        SELECT album_id, title
        FROM Albums
        WHERE artist_id = %s
    """,
        (artist_id,),
    )
    albums = cursor.fetchall()

    cursor.execute(
        """
        SELECT Songs.song_id, Songs.title, Artists.name
        FROM Songs
        JOIN Artists ON Songs.artist_id = Artists.artist_id
        WHERE Songs.artist_id = %s
    """,
        (artist_id,),
    )
    songs = cursor.fetchall()

    artist_details_window = Toplevel(main)
    artist_details_window.title(f"Künstler '{artist_name}'")

    window_width_artist_details = 400
    window_height_artist_details = 200

    x_position_artist_details = int(
        (screen_width / 2) - (window_width_artist_details / 2)
    )
    y_position_artist_details = int(
        (screen_height / 2) - (window_height_artist_details / 2)
    )

    artist_details_window.geometry(
        f"{window_width_artist_details}x{window_height_artist_details}+{x_position_artist_details}+{y_position_artist_details}"
    )
    artist_details_window.resizable(FALSE, FALSE)

    label_album = ttk.Label(artist_details_window, text="Alben:")
    label_album.grid(row=0, column=0)
    listbox_artist_albums = Listbox(artist_details_window, width=30)
    listbox_artist_albums.grid(row=1, column=0, padx=10)

    for album in albums:
        listbox_artist_albums.insert(END, album[1])

    label_song = ttk.Label(artist_details_window, text="Songs:")
    label_song.grid(row=0, column=1)
    listbox_artist_songs = Listbox(artist_details_window, width=30)
    listbox_artist_songs.grid(row=1, column=1, padx=5)

    for song in songs:
        listbox_artist_songs.insert(END, song[1])

    listbox_artist_songs.bind(
        "<Button-3>", lambda event: on_album_song_right_click(event, songs)
    )
    listbox_artist_albums.bind(
        "<Button-3>", lambda event: on_album_right_click(event, albums)
    )


def add_song_to_playlist(song_details_window, song_id):
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()
    if playlists:
        song_details_window.destroy()
        cursor.execute(
            "SELECT playlist_id, name FROM Playlists WHERE user_id = %s",
            (current_user_id,),
        )
        playlists = cursor.fetchall()

        playlist_window = Toplevel(main)
        playlist_window.title("Playlist auswählen")

        window_width_playlist = 400
        window_height_playlist = 300

        x_position_playlist = int((screen_width / 2) - (window_width_playlist / 2))
        y_position_playlist = int((screen_height / 2) - (window_height_playlist / 2))

        playlist_window.geometry(
            f"{window_width_playlist}x{window_height_playlist}+{x_position_playlist}+{y_position_playlist}"
        )
        playlist_window.resizable(FALSE, FALSE)

        listbox_playlists = Listbox(playlist_window, width=20, font="Helvetica 12")
        listbox_playlists.pack()

        for playlist in playlists:
            listbox_playlists.insert(END, playlist[1])

        button_open_playlist = ttk.Button(
            playlist_window,
            text="Playlist auswählen",
            command=lambda: add_song_to_selected_playlist(
                listbox_playlists, song_id, playlist_window
            ),
        )
        button_open_playlist.pack()
    else:
        messagebox.showwarning("Warnung", "Keine Playlists gefunden")


def add_song_to_selected_playlist(listbox_playlists, song_id, playlist_window):
    cursor.execute(
        "SELECT playlist_id, name FROM Playlists WHERE user_id = %s", (current_user_id,)
    )
    playlists = cursor.fetchall()
    selection = listbox_playlists.curselection()
    if selection:
        index = selection[0]
        playlist_id = playlists[index][0]
        try:
            cursor.execute(
                "INSERT INTO PlaylistSongs VALUES (%s, %s)", (playlist_id, song_id)
            )
            conn.commit()
            messagebox.showinfo("Erfolg", "Song zur Playlist hinzugefügt")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            messagebox.showinfo("Fehler", "Song bereits in der Playlist vorhanden")
        except psycopg2.Error as error:
            conn.rollback()
            messagebox.showerror(
                "Fehler",
                f"Song konnte nicht hinzugefügt werden: {error.diag.message_primary or str(error)}",
            )
    playlist_window.destroy()


def show_startup_error(title, error):
    error_window = Tk()
    error_window.withdraw()
    messagebox.showerror(title, str(error), parent=error_window)
    error_window.destroy()


def close_application():
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
    main.destroy()


def run_app():
    global conn, cursor, main, screen_width, screen_height
    global entry_username, entry_email, entry_password
    global entry_login_username, entry_login_password

    try:
        settings = DatabaseSettings.from_environment()
    except ValueError as error:
        show_startup_error("Konfiguration fehlt", error)
        return 1

    try:
        conn = psycopg2.connect(**settings.connection_parameters())
        cursor = conn.cursor()
    except psycopg2.Error as error:
        show_startup_error(
            "Datenbankverbindung fehlgeschlagen",
            error.diag.message_primary or str(error),
        )
        return 1

    main = Tk()
    main.title("Musik-DB")

    window_width = 260
    window_height = 350

    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()

    x_position = int((screen_width / 2) - (window_width / 2))
    y_position = int((screen_height / 2) - (window_height / 2))

    main.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    main.resizable(FALSE, FALSE)
    main.protocol("WM_DELETE_WINDOW", close_application)

    label_user_creation = ttk.Label(
        main, text="Erstellen eines Benutzers", font="Arial 12 bold"
    )
    label_user_creation.grid(row=0, column=0, columnspan=4, sticky="n", padx=20)

    label_username = ttk.Label(main, text="Benutzername:")
    label_username.grid(row=1, column=1, sticky="e")
    entry_username = ttk.Entry(main)
    entry_username.grid(row=1, column=2, columnspan=2, pady=10, padx=20, sticky="w")

    label_email = ttk.Label(main, text="E-Mail:")
    label_email.grid(row=2, column=1, sticky="e")
    entry_email = ttk.Entry(main)
    entry_email.grid(row=2, column=2, columnspan=2, pady=10, padx=20, sticky="w")

    label_password = ttk.Label(main, text="Passwort:")
    label_password.grid(row=3, column=1, sticky="e")
    entry_password = ttk.Entry(main, show="*")
    entry_password.grid(row=3, column=2, columnspan=2, pady=10, padx=20, sticky="w")

    button_insert = ttk.Button(main, text="Benutzer hinzufügen", command=insert_user)
    button_insert.grid(row=4, column=2, columnspan=2, pady=10)

    label_user_login = ttk.Label(main, text="Einloggen", font="Arial 12 bold")
    label_user_login.grid(row=5, column=0, columnspan=4, sticky="n", padx=20)

    label_login_username = ttk.Label(main, text="Benutzername\n oder E-Mail:")
    label_login_username.grid(row=6, column=1, sticky="e")
    entry_login_username = ttk.Entry(main)
    entry_login_username.grid(
        row=6, column=2, columnspan=2, pady=10, padx=20, sticky="w"
    )

    label_login_password = ttk.Label(main, text="Passwort:")
    label_login_password.grid(row=7, column=1, sticky="e")
    entry_login_password = ttk.Entry(main, show="*")
    entry_login_password.grid(
        row=7, column=2, columnspan=2, pady=10, padx=20, sticky="w"
    )

    button_login = ttk.Button(main, text="Login", command=login_user)
    button_login.grid(row=8, column=2, columnspan=2, pady=10)

    main.mainloop()
    return 0
