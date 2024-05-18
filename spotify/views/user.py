from decouple import config
from requests_oauthlib import OAuth2Session
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back.decorators import check_token

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=config('SPOTIFY_REDIRECT_URI'))

class UserView(APIView):
    @check_token
    def get(self, request):
        spotify_oauth.token = request.session.get('token')
        profile_response = spotify_oauth.get('https://api.spotify.com/v1/me')
        top_tracks_response = spotify_oauth.get('https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term&offset=0')
        top_artists_response = spotify_oauth.get('https://api.spotify.com/v1/me/top/artists?limit=5&time_range=long_term&offset=0')
        profile = profile_response.json()
        top_tracks = top_tracks_response.json()
        top_artists = top_artists_response.json()
        return Response({'user': profile, 'top_tracks': top_tracks, 'top_artists': top_artists})

class UserTracksView(APIView):
    @check_token
    def get(self, request):
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