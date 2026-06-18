from django.urls import path

from .web import user_controller

app_name = "users"

urlpatterns = [
    path("register/", user_controller.RegisterView.as_view(), name="register"),
    path("login/", user_controller.LoginView.as_view(), name="login"),
    path("logout/", user_controller.LogoutView.as_view(), name="logout"),
    path("profile/", user_controller.ProfileView.as_view(), name="profile"),
    path(
        "password/change/", user_controller.PasswordChangeView.as_view(), name="password-change"
    ),
    path("delete/", user_controller.DeleteAccountView.as_view(), name="delete-account"),
    path("players/", user_controller.PlayerListView.as_view(), name="player-list"),
    path("referees/", user_controller.RefereeListView.as_view(), name="referee-list"),
    path("users/", user_controller.UserListView.as_view(), name="user-list"),
]
