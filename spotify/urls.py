from django.urls import path

from spotify.views.auth import SpotifyAuthView, SpotifyCheckView, SpotifyLogoutView, SpotifyRedirectView
from spotify.views.playlist import PlaylistView
from spotify.views.user import UserTracksView, UserView

urlpatterns = [
    path('login/', SpotifyAuthView.as_view(), name='login'),
    path('redirect/', SpotifyRedirectView.as_view(), name='redirect'),
    path('logout/', SpotifyLogoutView.as_view(), name='logout'),
    path('check/', SpotifyCheckView.as_view(), name='check'),
    path('user/', UserView.as_view(), name='user'),
    path('user/tracks/', UserTracksView.as_view(), name='saved_tracks'),
    path('playlists/', PlaylistView.as_view(), name='playlists'),
]