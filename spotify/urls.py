from django.urls import path, re_path

from spotify.views.auth import SpotifyAuthView, SpotifyLogoutView, SpotifyRedirectView
from spotify.views.playlist import PlaylistView, SetlistView
from spotify.views.user import UserTracksView, UserView

urlpatterns = [
    path('login/', SpotifyAuthView.as_view(), name='login'),
    path('redirect/', SpotifyRedirectView.as_view(), name='redirect'),
    path('logout/', SpotifyLogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path('user/tracks/', UserTracksView.as_view(), name='saved_tracks'),
    path('playlists/', PlaylistView.as_view(), name='playlists'),
    re_path(r'^setlist/(?P<setlistId>[a-zA-Z0-9]*/$)', SetlistView.as_view(), name='setlist'),
]