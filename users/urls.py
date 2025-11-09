from django.urls import path
from .views import (
    RegisterView, LoginView,
    refresh_access_token, logout_view, profile_view
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", profile_view, name="profile"),
    path("refresh/", refresh_access_token, name="token_refresh_from_cookie"),
    path("logout/", logout_view, name="logout"),
]
