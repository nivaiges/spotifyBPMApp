from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


#find your spotify username at https://www.spotify.com/us/account/profile/
username = "22yq5rndcy2vf45jbyk3tv46a"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#print(client_id, client_secret)

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

token = get_token()
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"

    query_url = url + "?" + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists")
        return None
    
    return json_result[0]


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result






#print(token)
token = get_token()
result = search_for_artist(token, "ACDC")
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)
track_uris = []
for idx, song in enumerate(songs):
    track_uris.append(song['uri'])
    print(f"{idx + 1}. {song['name']}")



def create_playlist(token, username, playlist_name):
    url = f"https://api.spotify.com/v1/users/{username}/playlists"
    headers = get_auth_header(token)
    data = {
        "name": playlist_name,
        "public": True  # Set to True for a public playlist, or False for a private one
    }
    result = post(url, headers=headers, data=json.dumps(data))
    json_result = json.loads(result.content)
    print(json_result)
    playlist_id = json_result["id"]
    return playlist_id

def add_tracks_to_playlist(token, username, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {
        "uris": track_uris
    }
    result = post(url, headers=headers, data=json.dumps(data))
    if result.status_code == 201:
        print("Tracks added to the playlist successfully")
    else:
        print("Failed to add tracks to the playlist")

# Create a playlist
playlist_name = "Python Playlist"
playlist_id = create_playlist(token, username, playlist_name)

# Add tracks to the playlist
add_tracks_to_playlist(token, username, playlist_id, track_uris)