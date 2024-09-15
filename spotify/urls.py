from django.urls import re_path

from spotify.views.auth import SpotifyAuthView, SpotifyLogoutView, SpotifyRedirectView
from spotify.views.playlist import PlaylistView, SetlistView, TrackSearchView
from spotify.views.user import UserTracksView, UserView

urlpatterns = [
    re_path(r'^login/?$', SpotifyAuthView.as_view()),
    re_path(r'^redirect/?$', SpotifyRedirectView.as_view()),
    re_path(r'^logout/?$', SpotifyLogoutView.as_view()),
    re_path(r'^user/?$', UserView.as_view()),
    re_path(r'^user/tracks/?$', UserTracksView.as_view()),
    re_path(r'^playlists/?$', PlaylistView.as_view()),
    re_path(r'^setlist/?$', SetlistView.as_view()),
    re_path(r'^song/?$', TrackSearchView.as_view()),
]