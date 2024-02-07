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
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f0f0f0;
            }
            h1 {
                font-size: 2rem;
                color: #333;
            }
            p {
                font-size: 1rem;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div>
            <h1>Welcome to My Website</h1>
            <p>This is a simple, elegant homepage.</p>
        </div>
    </body>
    </html>
    """

@app.route('/list')
def last_tracks():
    access_token = refresh_spotify_token()
    if not access_token:
        return 'Access token is missing or expired', 400
    
    headers = {"Authorization": f"Bearer {access_token}"}
    recently_played_url = "https://api.spotify.com/v1/me/player/recently-played?limit=10"
    response = requests.get(recently_played_url, headers=headers)
    if response.status_code != 200:
        return f"Failed to fetch recently played tracks: {response.text}", response.status_code
    
    data = response.json()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Last Played Tracks</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            ul { list-style-type: none; padding: 0; }
            li { margin-bottom: 10px; }
            a { text-decoration: none; color: #007BFF; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h2>Last Played Tracks</h2>
        <ul>
    """
    
    for item in data['items']:
        track_name = item['track']['name']
        artist_names = ", ".join([artist['name'] for artist in item['track']['artists']])
        spotify_url = item['track']['external_urls']['spotify']
        html_content += f'<li><a href="{spotify_url}" target="_blank">{track_name}</a> by {artist_names}</li>'
    
    html_content += """
        </ul>
    </body>
    </html>
    """
    
    return html_content


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
    app.run(debug=False)



