#Spoti2lite

# --------------- #
# Libraries

import tkinter as tk
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import time
from bs4 import BeautifulSoup
import threading

# Functions

def initialize_spotify(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_song(spotify, song_name):
    results = spotify.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track
    else:
        return None

def get_lyrics(genius_api_token, track_name, artist_name):
    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {genius_api_token}"}
    search_url = f"{base_url}/search"
    data = {'q': f"{track_name} {artist_name}"}
    
    response = requests.get(search_url, data=data, headers=headers)
    json_data = response.json()
    if json_data['response']['hits']:
        song_info = json_data['response']['hits'][0]['result']
        song_url = song_info['url']
        
        lyrics_response = requests.get(song_url)
        return parse_lyrics(lyrics_response.text)
    else:
        return "Lyrics not found."

def parse_lyrics(html):
    soup = BeautifulSoup(html, 'html.parser')
    lyrics_div = soup.find('div', class_='lyrics') or soup.find('div', class_='SongPage__Section__Container')
    lyrics = lyrics_div.get_text() if lyrics_div else "Error: Lyrics not found."
    return lyrics

def update_playback_time(playback_label):
    while True:
        current_time = time.strftime("%M:%S", time.gmtime(0))  # Placeholder for actual playback time
        playback_label.config(text=f"Playback Time: {current_time}")
        time.sleep(1)

# UI Scripts

class MusicApp(tk.Tk):
    def __init__(self, spotify, genius_api_token):
        super().__init__()
        self.title("Music Streaming App")
        self.geometry("800x600")
        self.spotify = spotify
        self.genius_api_token = genius_api_token
        self.create_widgets()
        self.playback_time_thread = threading.Thread(target=update_playback_time, args=(self.playback_label,))
        self.playback_time_thread.daemon = True
        self.playback_time_thread.start()

    def create_widgets(self):
        self.search_frame = tk.Frame(self, bg='lightgrey')
        self.lyrics_frame = tk.Frame(self, bg='white')
        self.playback_frame = tk.Frame(self, bg='lightblue')
        self.playlist_frame = tk.Frame(self, bg='lightgreen')

        self.search_frame.pack(fill=tk.BOTH, expand=True)
        self.lyrics_frame.pack(fill=tk.BOTH, expand=True)
        self.playback_frame.pack(fill=tk.BOTH, expand=True)
        self.playlist_frame.pack(fill=tk.BOTH, expand=True)

        self.search_entry = tk.Entry(self.search_frame, width=50)
        self.search_entry.pack(pady=20)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_song)
        self.search_button.pack(pady=10)

        self.lyrics_text = tk.Text(self.lyrics_frame, wrap=tk.WORD)
        self.lyrics_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.playback_label = tk.Label(self.playback_frame, text="Playback Time: 00:00")
        self.playback_label.pack(pady=20)

        self.playlist_box = tk.Listbox(self.playlist_frame)
        self.playlist_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def search_song(self):
        song_name = self.search_entry.get()
        track = search_song(self.spotify, song_name)
        if track:
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            
            lyrics = get_lyrics(self.genius_api_token, track_name, artist_name)
            self.lyrics_text.delete(1.0, tk.END)
            self.lyrics_text.insert(tk.END, lyrics)
            self.add_to_playlist(track_name)
        else:
            self.lyrics_text.delete(1.0, tk.END)
            self.lyrics_text.insert(tk.END, "Song not found.")

    def add_to_playlist(self, track_name):
        self.playlist_box.insert(tk.END, track_name)

if __name__ == "__main__":
    SPOTIFY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
    SPOTIFY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'
    GENIUS_API_TOKEN = 'YOUR_GENIUS_API_TOKEN'

    spotify = initialize_spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    
    app = MusicApp(spotify, GENIUS_API_TOKEN)
    app.mainloop()
