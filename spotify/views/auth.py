from decouple import config
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from homepagev3_back import settings

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_DEBUG_REDIRECT_URI') if settings.DEBUG else config('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTHORIZE_URL = config('SPOTIFY_AUTHORIZE_URL')
SPOTIFY_TOKEN_URL = config('SPOTIFY_TOKEN_URL')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=SPOTIFY_REDIRECT_URI)
spotify_http_auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

class SpotifyAuthView(APIView):
    def get(self, request):
        if 'token' in request.session:
            return Response({'loggedIn': True}, status=status.HTTP_200_OK)
        auth_url, state = spotify_oauth.authorization_url(SPOTIFY_AUTHORIZE_URL)
        return Response(auth_url)


class SpotifyRedirectView(APIView):
    def get(self, request):
        token = spotify_oauth.fetch_token(
            SPOTIFY_TOKEN_URL,
            auth=spotify_http_auth,
            code=request.query_params.get('code')
        )
        request.session['token'] = token
        spotify_oauth.token = token
        return HttpResponse(
            """
                <body>
                    <script type="text/javascript">
                        window.close()
                    </script>
                    <button type="button" onclick="window.close()">Click to Close</button>
                </body>
            """
        )

class SpotifyLogoutView(APIView):
    def get(self, request):
        del request.session['token']
        del request.session['expires_at']