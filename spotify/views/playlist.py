from decouple import config
from requests_oauthlib import OAuth2Session
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back.decorators import check_token

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=config('SPOTIFY_REDIRECT_URI'))

class PlaylistView(APIView):
    @check_token
    def get(self, request):
        spotify_oauth.token = request.session.get('token')
        user_playlists_response = spotify_oauth.get('https://api.spotify.com/v1/me/playlists?limit=50&offset=0')
        user_playlists_json = user_playlists_response.json()
        user_playlists = user_playlists_json.get('items', [])
        while 'next' in user_playlists_response.json() and user_playlists_response.json()['next']:
            user_playlists_response = spotify_oauth.get(user_playlists_response.json()['next'])
            user_playlists_json = user_playlists_response.json()
            user_playlists += user_playlists_json.get('items', [])
        return Response(user_playlists)

    @check_token
    def post(self, request):
        pass