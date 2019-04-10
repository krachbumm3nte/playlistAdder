import glob
import os
import sys
import tkinter
import tkinter as tk
from tkinter import messagebox

import spotipy
from config import *
import adder_utils
import config
import add_current
from remove_current import removetool

if __name__ == '__main__':

    arg = sys.argv[1]
    # arg not in ['-r', '-a', '-u'] or len(sys.argv) != 0:
    if False:
        # messagebox.showerror(title='Error!', message='wrong number of arguments')

        print("""
        Tis program takes one and only one argument:
            -r      removes the currently playing song from the current playlist
            -a      opens a window to add the current song to one of the users playlists
            -u      removes the users stored information (requires a login upon next start)
        
        """)
        sys.exit()


    # set up tkinter Window + root Frame
    window = adder_utils.prepare_window(title='spotify tool')
    window.withdraw()

    root = tkinter.Frame(window, width=window_width, height=800, bg=backgroundcolor)
    root.pack()

    if arg == '-u':
        """
        This Option will Reset The users cached information and all Spotify api tokens and then prompt for a 
        new user login.
        """
        for file in glob.glob(f'.cache-*'):
            print('removing: ', file)
            os.remove(file)
        tk.messagebox.showinfo(title='Done.', message='cached user Information deleted.')
        sys.exit()


    # Determine current User or ask for Input
    user_logged_in = False

    for file in os.listdir("./"):
        if file.startswith(".cache-"):
            config.user = file[file.find('-') + 1:]
            user_logged_in = True
            print('found user cache')
            break

    if not user_logged_in:
        config.user = adder_utils.ask_username()
        if user is None or user == '':
            sys.exit()

    # retrieve authorization token for current user
    token = adder_utils.prompt_for_user_token(username=user, access_scope=scope, client_id=c_id, client_secret=c_secret,
                                              redirect_uri=redirect)
    if not token:
        print('no token')
        sys.exit()
    # create connection to the Spotify API
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    print(sp._auth)

    currently_playing = sp.current_user_playing_track()

    # check if the connected user is currently playing anything
    if currently_playing is None:
        tk.messagebox.showerror(title="Not currently Playing", message=f"{user} is not currently playing music "
                                                                       f"through Spotify")
        sys.exit()

    song_id = currently_playing["item"]["id"]  # current songs spotify id
    song_name = currently_playing["item"]["name"]  # current songs title
    artist_name = currently_playing["item"]["artists"][0]["name"]  # display the first artist, if multiple are present
    cover_image_url = currently_playing["item"]["album"]["images"][0]["url"]  # album cover url

    # display album cover and song information atop the root Frame
    adder_utils.pack_song_info(master=root, imageurl=cover_image_url, songname=song_name, artist=artist_name)

    if arg == '-r':
        """
        This tool removes the currently playing song from the current playlist.
        """
        # abort procedure, if not currently playing from inside a playlist (e.g. when playing from artist or album)
        if currently_playing["context"]["type"] != 'playlist':
            tk.messagebox.showerror(title='Wrong Playback Context!', message='not currently playing from a playlist')
            sys.exit()

        list_id = currently_playing['context']['uri']
        list_name = sp.user_playlist(user=user, playlist_id=list_id)['name']

        # abort procedure if current playlist does not belong to user
        if currently_playing['context']['uri'].split(':')[2] != user:
            tk.messagebox.showerror(title='Not your playlist!',
                                    message=f'The Playlist {list_name} does not belong to {user}')
            sys.exit()

        removetool(master=root, list_id=list_id, list_name=list_name, song_id=song_id, spotipy_instance=sp)

    if arg == '-a':
        """
        This tool opens a selection window of the users playlists, from wich he can select the ones he wants to
        add the currently playing song to.
        the Window can be used by mouse or by the keys defined in config.py
        """
        add_current.AddSongTool(window=window, root=root, spotify_instance=sp, song_id=song_id,
                                songname=song_name, artist=artist_name)


    # Display the window and begin waiting for keyboard inputs
    window.deiconify()
    window.mainloop()
