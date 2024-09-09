import json
import urllib

import requests
from decouple import config
from django.shortcuts import redirect
from oauthlib.oauth2 import TokenExpiredError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back import settings
from spotify.views.auth import spotify_oauth

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_DEBUG_REDIRECT_URI') if settings.DEBUG else config('SPOTIFY_REDIRECT_URI')
SPOTIFY_TOKEN_URL = config('SPOTIFY_TOKEN_URL')
SETLIST_FM_KEY = config('SETLIST_FM_KEY')

class PlaylistView(APIView):
    def get(self, request):
        if 'token' in request.session:
            spotify_oauth.token = request.session.get('token')
            try:
                user_playlists_response = spotify_oauth.get('https://api.spotify.com/v1/me/playlists?limit=50&offset=0')
            except TokenExpiredError:
                token = spotify_oauth.refresh_token(
                    SPOTIFY_TOKEN_URL,
                    refresh_token=spotify_oauth.token.get('refresh_token'),
                    body={
                        'client_id': SPOTIFY_CLIENT_ID,
                        'refresh_token': spotify_oauth.token.get('refresh_token'),
                        'grant_type': 'refresh_token'
                    }
                )
                request.session['token'] = token
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
                try:
                    playlist_response = spotify_oauth.post(
                        f'https://api.spotify.com/v1/users/{request_data["id"]}/playlists',
                        data=json.dumps(playlist_data)
                    )
                except TokenExpiredError:
                    token = spotify_oauth.refresh_token(
                        SPOTIFY_TOKEN_URL,
                        refresh_token=spotify_oauth.token.get('refresh_token'),
                        body={
                            'client_id': SPOTIFY_CLIENT_ID,
                            'refresh_token': spotify_oauth.token.get('refresh_token'),
                            'grant_type': 'refresh_token'
                        }
                    )
                    request.session['token'] = token
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
    def get(self, request):
        setlist_id = request.query_params['setlistId']
        setlist_response = requests.get(f'https://api.setlist.fm/rest/1.0/setlist/{setlist_id}', headers={'Accept': 'application/json', 'x-api-key': SETLIST_FM_KEY})
        return Response(setlist_response.json())

class TrackSearchView(APIView):
    def get(self, request):
        spotify_oauth.token = request.session.get('token')
        track_query = urllib.parse.quote(request.query_params.get('track'))
        artist_query = urllib.parse.quote(request.query_params.get('artist'))
        search_url = f'https://api.spotify.com/v1/search?q=track%3{track_query}'
        if artist_query:
            search_url += f'%2520artist%3{artist_query}'
        search_url += f'&type=track&limit=5'
        search_response = spotify_oauth.get(search_url)
        response_json = search_response.json()
        tracks = []
        if response_json.get('tracks'):
            for track in response_json.get('tracks', {}).get('items'):
                new_track = {
                    'album': {'name': track.get('album', {}).get('name')},
                    'id': track.get('id'),
                    'name': track.get('name')
                }
                tracks.append(new_track)
        return Response(tracks)
