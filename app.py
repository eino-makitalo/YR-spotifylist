import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, render_template
import requests
import json

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))  # Use environment variable or generate a random secret key



# Spotify URLs and credentials from environment variables
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_RECENTLY_PLAYED_URL = 'https://api.spotify.com/v1/me/player/recently-played'
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = "user-read-recently-played"

def refresh_spotify_token():
    """Refresh the Spotify access token using the stored refresh token."""
    refresh_token = open('spotify_refresh_token.txt').read().strip()
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        # Print or log the error response from Spotify
        print("Failed to refresh token:", response.json())
        raise Exception("Could not refresh token. Spotify response: " + str(response.json()))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/list')
def last_tracks():
    access_token = refresh_spotify_token()
    if not access_token:
        return 'Access token is missing or expired', 400

    headers = {"Authorization": f"Bearer {access_token}"}
    recently_played_url = "https://api.spotify.com/v1/me/player/recently-played?limit=20"
    response = requests.get(recently_played_url, headers=headers)
    if response.status_code != 200:
        return f"Failed to fetch recently played tracks: {response.text}", response.status_code

    data = response.json()
    track_details = {}
    for item in data['items']:
        track_name = item['track']['name']
        track_url = item['track']['external_urls']['spotify']
        # If the track name is already in the dictionary, increment its count
        if track_name in track_details:
            track_details[track_name]['count'] += 1
        else:
            # Otherwise, add the track to the dictionary with count 1 and store its URL
            track_details[track_name] = {'count': 1, 'url': track_url}

    # Convert the track_details dictionary to a list of dictionaries for the template
    tracks_info = [{'name': name, 'count': details['count'], 'url': details['url']} for name, details in track_details.items()]

    return render_template('last_tracks.html', tracks=tracks_info)

@app.route('/authYR12')
def initialize_auth():
    # Redirect user to Spotify authorization page
    auth_url = f"{SPOTIFY_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_token_url = SPOTIFY_TOKEN_URL
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    post_request = requests.post(auth_token_url, data=payload)
    response_data = post_request.json()
    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')

    if refresh_token:
        # Here you save the refresh token for future use
        with open('spotify_refresh_token.txt', 'w') as file:
            file.write(refresh_token)
        return 'Refresh token successfully obtained and saved!'
    else:
        return 'Failed to obtain refresh token'



if __name__ == '__main__':
    app.run(debug=True)



