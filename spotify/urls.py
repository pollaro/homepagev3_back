from django.urls import path

from spotify.views.auth import SpotifyAuthView, SpotifyLogoutView, SpotifyRedirectView

urlpatterns = [
    path('login/', SpotifyAuthView.as_view(), name='login'),
    path('redirect/', SpotifyRedirectView.as_view(), name='redirect'),
    path('logout/', SpotifyLogoutView.as_view(), name='logout'),
    path('check/', SpotifyCheckView.as_view(), name='check'),
    path('user/', ),
    path('playlist/',),
    path('saved/', )
]