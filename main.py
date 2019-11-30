import glob
import os
import sys
import tkinter as tk
import argparse
import spotipy
from config import *
import adder_utils
import config
import add_current
from remove_current import removetool


def prepare_window():
    """
    Prepare a tkinter Window for the app and set relevant parameters
    :return:
    """
    window = tk.Tk()
    window.title('spotify tool')
    window.geometry(f"+0+0")
    print(window.winfo_screenmmheight())
    window.wm_attributes("-topmost", 1)
    window.focus_force()
    window.resizable(False, True)
    return window


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    modeselect = parser.add_mutually_exclusive_group()

    modeselect.add_argument('-r', '--remove', action='store_true', help='removes the playing song from the current playback environment')
    modeselect.add_argument('-a', '--add', action='store_true', help='opens a selection window to add the current song to one of the user\'s playlists')
    modeselect.add_argument('-u', '--unlink', action='store_true', help='unlinks the current account from this application')

    args = parser.parse_args()

    # set up tkinter Window + root Frame
    window = prepare_window()
    window.withdraw()

    root = tk.Frame(window, width=window_width, height=800, bg=backgroundcolor)
    root.pack()

    if args.unlink:
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
            print(f'found user cache for {config.user}')
            break

    if not user_logged_in:
        config.user = adder_utils.ask_username()
        print(config.user)
        if config.user is None or config.user == '':
            sys.exit()
    # retrieve authorization token for current user
    token = adder_utils.prompt_for_user_token(username=config.user, access_scope=scope, client_id=c_id, client_secret=c_secret,
                                              redirect_uri=redirect)
    if not token:
        print('no token')
        sys.exit()
    # create connection to the Spotify API
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    currently_playing = sp.current_user_playing_track()

    # check if the connected user is currently playing anything
    if currently_playing is None:
        tk.messagebox.showerror(title="Not currently Playing", message=f"{config.user} is not currently playing music "
                                                                       f"through Spotify")
        sys.exit()

    song_id = currently_playing["item"]["id"]  # current songs spotify id
    song_name = currently_playing["item"]["name"]  # current songs title
    artist_names = [x["name"] for x in currently_playing["item"]["artists"]]
    artist_names = ','.join([x for x in artist_names])

    cover_image_url = currently_playing["item"]["album"]["images"][0]["url"]  # album cover url
    print(f'currently playing {song_name} by {artist_names}')

    # display album cover and song information atop the root Frame
    adder_utils.pack_song_info(master=root, imageurl=cover_image_url, songname=song_name, artist=artist_names)

    if args.remove:
        """
        This tool removes the currently playing song from the current playlist.
        """

        window.title('remove current song')

        # abort procedure, if not currently playing from inside a playlist (e.g. when playing from artist or album)
        if currently_playing["context"]["type"] != 'playlist':
            tk.messagebox.showerror(title='Wrong Playback Context!', message='not currently playing from a playlist')
            sys.exit()

        list_id = currently_playing['context']['uri']
        list_name = sp.user_playlist(user=config.user, playlist_id=list_id)['name']

        # abort procedure if current playlist does not belong to user
        if currently_playing['context']['uri'].split(':')[2] != config.user:
            tk.messagebox.showerror(title='Not your playlist!',
                                    message=f'The Playlist {list_name} does not belong to {config.user}')
            sys.exit()

        removetool(master=root, list_id=list_id, list_name=list_name, song_id=song_id, spotipy_instance=sp)

    elif args.add:
        """
        This tool opens a selection window of the users playlists, from wich he can select the ones he wants to
        add the currently playing song to.
        the Window can be used by mouse or by the keys defined in config.py
        """

        window.title('add current song to playlists')

        add_current.AddSongTool(window=window, root=root, spotify_instance=sp, song_id=song_id,
                                songname=song_name, artist=artist_names)


    # Display the window and begin waiting for keyboard inputs
    window.deiconify()
    window.mainloop()
