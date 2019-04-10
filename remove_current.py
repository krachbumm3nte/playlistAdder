from functools import partial

from adder_utils import *


def removetool(master, list_id, list_name, song_id, spotipy_instance):

    removefunc = partial(remove_song_from, song_id, list_id, spotipy_instance)

    query, query_label = continue_query(querytext=f"remove this song from {list_name}?", master=master,
                                        cancel_func=sys.exit, continue_func=removefunc)
    query.pack()
    query.focus_set()


def remove_song_from(song_id, list_id, spotipy_instance, event=None):
    spotipy_instance.user_playlist_remove_all_occurrences_of_tracks(user=user, playlist_id=list_id, tracks=[song_id])
    sys.exit()
