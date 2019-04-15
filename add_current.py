from adder_utils import *
from config import *


class AddSongTool:

    def __init__(self, window, root, spotify_instance, song_id, songname, artist):
        self.artist = artist
        self.song_id = song_id
        self.songname = songname
        self.spotify_instance = spotify_instance
        self.buttonlist = {}
        self.selectedplaylists = []
        self.duplicatelists = []


        window.bind(key_movelistup, self.moveListUp)
        window.bind(key_movelistdown, self.moveListDown)
        window.bind(key_confirm_selection, self.process_selection)
        self.window = window

        # retrieve and display Playlists
        playlistresponse = spotify_instance.user_playlists('krachbumm3nte')
        self.playlist_dict = dict()

        self.listcontainer = tk.Listbox(master=root, bg=backgroundcolor, selectmode='multiple', fg=textcolor, height=36, exportselection=0)
        self.listcontainer.pack(expand=1, fill=tk.BOTH, padx=5)
        self.listcontainer.bind(sequence=key_escape, func=sys.exit)
        self.listcontainer.focus_force()

        # create the list of buttons representing each playlist, displayed in the main window
        for item in playlistresponse["items"]:
            if item['owner']['display_name'] == user:

                name = item["name"]
                playlist_id = item["id"]
                self.playlist_dict[name] = playlist_id
                self.listcontainer.insert(tk.END, name)

        # creating the Frame that holds the confirmation query for adding to a playlist
        self.continuequery, self.query_label = continue_query(querytext='', master=root, cancel_func=self.returnToList,
                                                              continue_func=self.add_current_song_to_seleted)
        self.returnToList()

    def moveListUp(self, event=None):
        self.window.event_generate('<Shift-Tab>')

    def moveListDown(self, event=None):
        self.window.event_generate('<Tab>')

    def add_current_song_to_seleted(self, event=None):
        for list_name in self.selectedplaylists:
            print(f'adding Song to {list_name}')
            self.spotify_instance.user_playlist_add_tracks(user, self.playlist_dict[list_name], [self.song_id])
        sys.exit()

    def process_selection(self, event=None):
        self.selectedplaylists.clear()
        self.duplicatelists.clear()

        for index in self.listcontainer.curselection():
            name=self.listcontainer.get(index)
            if self.playlistcontainstrack(pl_id=self.playlist_dict[name], t_id=self.song_id,
                                          spotify_instance=self.spotify_instance):
                self.duplicatelists.append(name)
            else:
                self.selectedplaylists.append(name)

        self.query_label.configure(text=self.format_query_string())
        self.continuequery.pack()
        self.continuequery.focus_set()

    def returnToList(self, event=None):
        self.continuequery.pack_forget()
        self.listcontainer.pack(expand=1, fill=tk.BOTH, padx=5)
        self.listcontainer.focus_force()

    def playlistcontainstrack(self, pl_id, t_id, spotify_instance):
        listresponse = spotify_instance.user_playlist(user, pl_id)
        for track in listresponse['tracks']['items']:
            if track['track']['id'] == t_id:
                return True
        return False

    def format_query_string(self):
        selected_count = len(self.selectedplaylists)
        duplicate_count = len(self.duplicatelists)

        querytext = ""

        if selected_count == 0:
            if duplicate_count == 0:
                return
            elif duplicate_count == 1:
                querytext += f"{self.duplicatelists[0]} already contains {self.songname}!"
            else:
                querytext += 'all playlists already contain this song.'
        self.listcontainer.pack_forget()

        if selected_count > 0:
            querytext += "will be added to the following playlist" + (
                's' if len(self.selectedplaylists) > 0 else str) + ":\n"
            for n in self.selectedplaylists:
                querytext += f"\t {n}\n"
            if len(self.duplicatelists) > 0:
                querytext += f"the current song is already contained in:\n"
            for n in self.duplicatelists:
                querytext += f"\t {n}\n"

        return querytext
