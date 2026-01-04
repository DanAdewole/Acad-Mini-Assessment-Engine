from django.urls import path

from .views import (
    ChangePasswordView,
    CurrentUserView,
    LoginView,
    LogoutView,
    RegisterView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
