from functools import partial

import config
from adder_utils import *


def removetool(master, list_id, list_name, song_id, spotipy_instance):

    removefunc = partial(remove_song_from, song_id, list_id, spotipy_instance, list_name)

    query, query_label = continue_query(querytext=f"remove this song from {list_name}?", master=master,
                                        cancel_func=sys.exit, continue_func=removefunc)
    query.pack()
    query.focus_set()


def remove_song_from(song_id, list_id, spotipy_instance, list_name, event=None):
    spotipy_instance.user_playlist_remove_all_occurrences_of_tracks(user=config.user,
                                                                    playlist_id=list_id, tracks=[song_id])
    print(f'removed song from {list_name}')
    sys.exit()
