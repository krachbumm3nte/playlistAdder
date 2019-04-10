import io
import os
import sys
import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog
from urllib.request import urlopen

import PIL.Image
import PIL.ImageTk
import spotipy
from spotipy import oauth2

from config import *


def ask_username():
    return tk.simpledialog.askstring(title='Enter Username', prompt='Enter your Spotify Username:')


# Prepare a tkinter Window used to display the app in
def prepare_window(title):
    window = tk.Tk()
    window.title(title)
    window.wm_attributes("-topmost", 1)
    window.focus_force()
    return window


def continue_query(querytext, master, cancel_func, continue_func):
    query_frame = tk.Frame(master=master, bg=backgroundcolor, width=window_width, pady=25)
    info_label = tk.Label(master=query_frame, text=querytext, justify="left", anchor="w",
                          fg=textcolor, bg=backgroundcolor)
    info_label.config(font=("Helvetica", 12))
    info_label.pack()

    cancel_button = tk.Button(master=query_frame, command=cancel_func, text=f"cancel {key_escape}", anchor="w",
                              fg=textcolor, bg=backgroundcolor, activeforeground=selected_text_color, padx=13, pady=12)
    cancel_button.pack(side=tk.LEFT)
    query_frame.bind(key_escape, cancel_func)

    confirm_button = tk.Button(master=query_frame, command=continue_func, text=f"confirm {key_confirm}", anchor="e",
                               fg=textcolor, bg=backgroundcolor, activeforeground=selected_text_color, padx=13, pady=12)
    confirm_button.pack(side=tk.RIGHT)
    query_frame.bind(key_confirm, continue_func)

    return query_frame, info_label


# Display @imageurl, @songname and @artist at the top of the @master Tkinter Widget
def pack_song_info(master, imageurl, songname, artist):

    # retrieve the album cover image and display it
    image_byt = urlopen(imageurl).read()
    coverimage = PIL.Image.open(io.BytesIO(image_byt))
    coverimage = coverimage.resize((image_size, image_size), PIL.Image.ANTIALIAS)
    photo = PIL.ImageTk.PhotoImage(coverimage)
    panel = tk.Label(master=master, image=photo, justify="left", anchor="w", bg=backgroundcolor)
    panel.pack(pady=10, anchor="w", padx=15)
    panel.image = photo

    # Display Title and Artist
    track_label = tk.Label(master=master, text=songname[0:20], anchor="w", fg=textcolor, bg=backgroundcolor, padx=15)
    track_label.config(font=("Helvetica", 24))
    track_label.pack(anchor="w")

    artist_label = tk.Label(master=master, text=artist, anchor="w", fg=textcolor, bg=backgroundcolor, padx=30, pady=10)
    artist_label.config(font=("Helvetica", 18))
    artist_label.pack(anchor="w")


def prompt_for_user_token(username, access_scope=None, client_id=None,
                          client_secret=None, redirect_uri=None, cache_path=None):
    """ prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens

    """

    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not client_id:
        print('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:

            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

            Get your credentials at     
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    cache_path = cache_path or ".cache-" + username
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
                                           scope=access_scope, cache_path=cache_path)

    # try to get a valid token for this user from the cache.
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print('starting authentication process...')
        auth_url = sp_oauth.get_authorize_url()
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            tkinter.messagebox.showerror(title="Error opening browser",
                                         message=f"Could not open a webbrowser, "
                                                 f"please navigate to this URL:\n{auth_url}")

        response = tkinter.simpledialog.askstring(title='Enter URL', prompt="Enter the URl you were redirected to "
                                                                            "after logging in (if you were already "
                                                                            "logged into spotify in your browser you "
                                                                            "were redirected directly):")

        if response is None or response == '':
            sys.exit()

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

        # Auth'ed API request
        if token_info:
            tk.messagebox.showinfo(title='Success!', message='Successfully linked your Spotify account to this app!'
                                                             'undo this by running this ap with the argument -u '
                                                             'or deleting the .cache file in this directory')
        else:
            tk.messagebox.showerror(title='Authentication failed')
            return None

    return token_info['access_token']
