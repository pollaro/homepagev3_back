from datetime import datetime

from decouple import config
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back import settings

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_DEBUG_REDIRECT_URI') if settings.DEBUG else config('SPOTIFY_REDIRECT_URI')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=SPOTIFY_REDIRECT_URI)
spotify_http_auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

class SpotifyAuthView(APIView):
    def get(self, request):
        auth_url, state = spotify_oauth.authorization_url(SPOTIFY_REDIRECT_URI)
        return Response(auth_url)

class SpotifyRedirectView(APIView):
    def get(self, request):
        token = spotify_oauth.fetch_token(
            'https://accounts.spotify.com/api/token',
            auth=spotify_http_auth,
            authorize_url=request.data
        )
        request.session['token'] = token
        request.session['expires_at'] = datetime.now() + token['expires_in']

class SpotifyLogoutView(APIView):
    def get(self, request):
        del request.session['token']
        del request.session['expires_at']

class SpotifyCheckView(APIView):
    def get(self, request):
        if 'token' in request.session:
            return Response(True)
        return Response(False)