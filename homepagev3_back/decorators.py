import functools
from datetime import datetime, timedelta

from decouple import config
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = config('SPOTIFY_SCOPE')

spotify_oauth = OAuth2Session(SPOTIFY_CLIENT_ID, scope=SPOTIFY_SCOPE, redirect_uri=config('SPOTIFY_REDIRECT_URI'))
spotify_http_auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

def check_token(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        time_now = datetime.now()
        if time_now > datetime.fromisoformat(request.session.get('expires_at')):
            original_token = request.session.get('token')
            token = spotify_oauth.refresh_token(
                'https://accounts.spotify.com/api/token',
                auth=spotify_http_auth,
                body={'grant_type': 'refresh_token'},
                refresh_token=original_token.get('refresh_token')
            )
            expire_time = datetime.now() + timedelta(seconds=token.get('expires_in'))
            request.session['token'] = token
            request.session['expires_at'] = expire_time.isoformat()
        return func(self, request, *args, **kwargs)
    return wrapper