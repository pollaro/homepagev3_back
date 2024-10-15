from django.urls import re_path

from hbl.views.auth_views import CheckedLoggedIn, GetUserView, OauthView, RedirectURIView

urlpatterns = [
    re_path(r'^login/?$', OauthView.as_view()),
    re_path(r'^redirect/?$', RedirectURIView.as_view()),
    re_path(r'^check/?$', CheckedLoggedIn.as_view()),
    re_path(r'^get_user/?$', GetUserView.as_view()),
]