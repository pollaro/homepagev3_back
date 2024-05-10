from decouple import config
from requests_oauthlib import OAuth2Session
from rest_framework.views import APIView

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=SPOTIFY_REDIRECT_URI)

class PlaylistView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass
