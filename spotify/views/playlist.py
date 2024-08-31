import json

import requests
from decouple import config
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back import settings
from spotify.views.auth import SpotifyAuthView

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_DEBUG_REDIRECT_URI') if settings.DEBUG else config('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTHORIZE_URL = config('SPOTIFY_AUTHORIZE_URL')
SETLIST_FM_KEY = config('SETLIST_FM_KEY')

spotify_oauth = OAuth2Session(
    SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    auto_refresh_url=SPOTIFY_AUTHORIZE_URL,
    token_updater=SpotifyAuthView.save_token
)

class PlaylistView(APIView):
    def get(self, request):
        if 'token' in request.session:
            spotify_oauth.token = request.session.get('token')
            user_playlists_response = spotify_oauth.get('https://api.spotify.com/v1/me/playlists?limit=50&offset=0')
            user_playlists_json = user_playlists_response.json()
            user_playlists = user_playlists_json.get('items', [])
            while 'next' in user_playlists_response.json() and user_playlists_response.json()['next']:
                user_playlists_response = spotify_oauth.get(user_playlists_response.json()['next'])
                user_playlists_json = user_playlists_response.json()
                user_playlists += user_playlists_json.get('items', [])
            return Response(user_playlists)
        return redirect('spotify/login/')

    def post(self, request):
        if 'token' in request.session:
            spotify_oauth.token = request.session.get('token')
            request_data = request.data.get('playlist')
            if request_data:
                tracks = request_data.get('tracks')
                playlist_data = {
                    'name': request_data.get('name'),
                    'public': request_data.get('public', False),
                    'description': request_data.get('description')
                }
                playlist_response = spotify_oauth.post(
                    f'https://api.spotify.com/v1/users/{request_data["id"]}/playlists',
                    data=json.dumps(playlist_data)
                )
                uris = [track['uri'] for track in tracks]
                responses = []
                while len(uris) > 0:
                    add_tracks_data = {
                        'uris': uris[:100]
                    }
                    uris = uris[100:]
                    post_response = spotify_oauth.post(
                        f'https://api.spotify.com/v1/playlists/{playlist_response.json()["id"]}/tracks',
                        data=json.dumps(add_tracks_data)
                    )
                    responses.append(post_response.status_code == status.HTTP_201_CREATED)
                if all(responses):
                    return Response(status.HTTP_201_CREATED)
                return Response(responses, status=status.HTTP_400_BAD_REQUEST)
        return redirect('spotify/login/')

class SetlistView(APIView):
    def get(self, request, setlist_id):
        setlist_response = requests.get(f'https://api.setlist.fm/1.0/setlist/{setlist_id}', headers={'Accept': 'application/json', 'x-api-key': SETLIST_FM_KEY})
        setlist_json = setlist_response.json()
        return Response(setlist_json)
