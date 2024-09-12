from decouple import config
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back import settings
from spotify.views.auth import spotify_oauth

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_DEBUG_REDIRECT_URI') if settings.DEBUG else config('SPOTIFY_REDIRECT_URI')
SPOTIFY_TOKEN_URL = config('SPOTIFY_TOKEN_URL')

class UserView(APIView):
    def get(self, request):
        if 'token' in request.session:
            spotify_oauth.token = request.session.get('token')
            profile_response = spotify_oauth.get('https://api.spotify.com/v1/me')
            top_tracks_response = spotify_oauth.get('https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term&offset=0')
            top_artists_response = spotify_oauth.get('https://api.spotify.com/v1/me/top/artists?limit=5&time_range=long_term&offset=0')
            profile = profile_response.json()
            top_tracks = top_tracks_response.json()
            top_artists = top_artists_response.json()
            return Response({'user': profile, 'top_tracks': top_tracks, 'top_artists': top_artists})
        return redirect('spotify/login/')

class UserTracksView(APIView):
    def get(self, request):
        if 'token' in request.session:
            spotify_oauth.token = request.session.get('token')
            market = request.query_params.get('market')
            saved_tracks_response = spotify_oauth.get(f'https://api.spotify.com/v1/me/tracks?limit=50&offset=0&market={market}')
            saved_tracks_json = saved_tracks_response.json()
            saved_tracks = saved_tracks_json.get('items', [])
            while 'next' in saved_tracks_response.json() and saved_tracks_response.json()['next']:
                saved_tracks_response = spotify_oauth.get(saved_tracks_response.json()['next'])
                saved_tracks_json = saved_tracks_response.json()
                saved_tracks += saved_tracks_json.get('items', [])
            return Response(saved_tracks)
        return redirect('spotify/login/')