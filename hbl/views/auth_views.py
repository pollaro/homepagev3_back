import logging

import xmltodict
from decouple import config
from django.conf import settings
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

redirect_uri = (
    config("YAHOO_REDIRECT_URI_DEBUG")
    if settings.DEBUG
    else config("YAHOO_REDIRECT_URI")
)
yahoo_oauth = OAuth2Session(
    client_id=config('YAHOO_CLIENT_ID'),
    redirect_uri=redirect_uri,
    auto_refresh_url='https://api.login.yahoo.com/oauth2/get_token',
    auto_refresh_kwargs={
        'client_id': config('YAHOO_CLIENT_ID'),
        'client_secret': config('YAHOO_CLIENT_SECRET'),
        'redirect_uri': 'oob',
        'grant_type': 'refresh_token',
    }
)

def token_updater(token):
    yahoo_oauth.token = token
yahoo_oauth.token_updater = token_updater

class OauthView(APIView):
    """
    This view that starts yahoo oauth process
    """

    def get(self, request):
        auth_url, state = yahoo_oauth.authorization_url(
            "https://api.login.yahoo.com/oauth2/request_auth"
        )
        return Response(auth_url)


class RedirectURIView(APIView):
    """
    This view is where yahoo sends token code back, gets the real token, and closes oauth pop-up
    """

    def get(self, request):
        code = request.query_params.get("code")
        if code:
            token = yahoo_oauth.fetch_token(
                "https://api.login.yahoo.com/oauth2/get_token",
                authorization_response=redirect_uri,
                code=code,
                client_secret=config("YAHOO_CLIENT_SECRET"),
            )
            return HttpResponse(
                """
                    <body>
                        <script>
                            window.close()
                        </script>
                    </body>
                """
            )


class CheckedLoggedIn(APIView):
    def get(self, request):
        if yahoo_oauth.authorized:
            try:
                user_guid_xml = yahoo_oauth.get(
                    f'{config("YAHOO_SPORTS_API")}/users;use_login=1',
                )
                response_dict = xmltodict.parse(user_guid_xml.text)
                jimOrGreg = response_dict['fantasy_content']['users']['user']['guid'] in [config('GREG_GUID'), config('JIM_GUID')]
                return Response({
                    'loggedIn': yahoo_oauth.authorized,
                    'user': response_dict['fantasy_content']['users']['user']['guid'],
                    'jimOrGreg': jimOrGreg
                })
            except Exception as e:
                raise Exception(e)
        return Response({'loggedIn': False, 'user': None})


class GetUserView(APIView):
    def get(self, request):
        try:
            user_guid_xml = yahoo_oauth.get(
                f'{config("YAHOO_SPORTS_API")}/users;use_login=1',
            )
            response_dict = xmltodict.parse(user_guid_xml.text)
            return response_dict["fantasy_content"]["users"]["user"]["guid"]
        except Exception as e:
            return None