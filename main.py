from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import streamlit as st


load_dotenv()
st.set_page_config(
    page_title='Spotify BPM Playlist Maker',
    page_icon='🎵',
    layout='wide'
)

# find your spotify username at https://www.spotify.com/us/account/profile/
username = "22yq5rndcy2vf45jbyk3tv46a"
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# print(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)


def get_token():
    auth_string = SPOTIPY_CLIENT_ID + ":" + SPOTIPY_CLIENT_SECRET
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


def genre_List():
    url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["genres"]
    return json_result


genreListObj = genre_List()
# print(genreListObj)
st.title('This is a title')
options = st.multiselect('Select playlist genres:', genreListObj)
playlistName = st.text_input(label="Name You want your playlist to be Called",
                             max_chars=100, placeholder="A Python Playlist")
min_Input = round(st.number_input(label='Min BPM', min_value=0), 2)
max_Input = round(st.number_input(label='Max BPM', min_value=0), 2)


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists")
        return None

    return json_result[0]


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{
        artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


# print(token)
token = get_token()
result = search_for_artist(token, "ACDC")
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)
track_uris = []
for idx, song in enumerate(songs):
    track_uris.append(song['uri'])
   # print(f"{idx + 1}. {song['name']}")

# Read Your library, Create a playlist, Populate playlist based on your seed (music you like)
scope = ["user-library-read", "playlist-modify-private", "user-read-private"]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
sp2 = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
    )
)

user_info = sp2.current_user()
user_id = user_info["id"]

print(f"User ID: {user_id}")
results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    # print(idx, track['artists'][0]['name'], " – ", track['name'])


def user_playlist_create(user_id, playlistName, public=False, collaborative=False, description="A Python Playlist"):

    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlistName,
        public=public,
        collaborative=collaborative,
        description=description
    )
    return playlist


# created_playlist = user_playlist_create(user_id, "Python Playlist", public=False, collaborative=False, description='A Test Python Playlist')
# print(created_playlist)

# seed_track_id


def get_recommendations_with_bpm(seed_genres, min_bpm, max_bpm, market, limit=20):
    try:
        # Get a list of recommended tracks
        seed_genres_list = seed_genres.split(",")

        recommendations = sp2.recommendations(
            seed_genres=seed_genres_list,
            min_tempo=min_bpm,
            max_tempo=max_bpm,
            target_tempo=((max_bpm+min_bpm)/2),
            market=market,
            limit=limit
        )
        track_uri = [track[uri] for track in recommendations['tracks']]
        return track_uri

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def makeUserPlaylist(genres, minTempo, maxTempo, country):
    get_recommendations_with_bpm(genres, minTempo, maxTempo, "ES")
    newPlaylist = user_playlist_create(user_id, playlistName, False, False,
                                       description=f"A Playlist with songs having a bpm range of {minTempo} to {maxTempo}")
    if track_uris:
        # Add the recommended tracks to the user's playlist
        sp.playlist_add_items(newPlaylist['id'], track_uris)
        return f"Playlist '{playlistName}' created with {len(track_uris)} tracks."
    else:
        return "No tracks were found."


if st.button(label="Go"):
    makeUserPlaylist(options, min_Input, max_Input, "ES")


# recommended_tracks = get_recommendations_with_bpm("soul", min_bpm, max_bpm, "ES", limit=10)

"""if recommended_tracks:
    print("Recommended Tracks:")
    for track in recommended_tracks['tracks']:
        print(f"{track['name']} by {track['artists'][0]['name']}")"""


# lookup = get_recommendations_with_bpm(120, 150, 20)
# print(lookup)
