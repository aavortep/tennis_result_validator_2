from django.urls import path

from .web import tournament_controller

app_name = "tournaments"

urlpatterns = [
    path("", tournament_controller.TournamentListCreateView.as_view(), name="tournament-list"),
    path("<int:pk>/", tournament_controller.TournamentDetailView.as_view(), name="tournament-detail"),
    path(
        "<int:pk>/add-player/",
        tournament_controller.TournamentAddPlayerView.as_view(),
        name="add-player",
    ),
    path(
        "<int:pk>/remove-player/<int:player_id>/",
        tournament_controller.TournamentRemovePlayerView.as_view(),
        name="remove-player",
    ),
    path(
        "<int:pk>/add-referee/",
        tournament_controller.TournamentAddRefereeView.as_view(),
        name="add-referee",
    ),
    path(
        "<int:pk>/status/",
        tournament_controller.TournamentStatusView.as_view(),
        name="tournament-status",
    ),
    path(
        "<int:pk>/matches/",
        tournament_controller.TournamentMatchesView.as_view(),
        name="tournament-matches",
    ),
]
