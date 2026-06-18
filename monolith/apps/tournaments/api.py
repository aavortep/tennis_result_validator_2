from django.urls import path

from .web import match_controller, tournament_controller

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
    path("matches/", match_controller.MatchListCreateView.as_view(), name="match-list"),
    path("matches/<int:pk>/", match_controller.MatchDetailView.as_view(), name="match-detail"),
    path("matches/my-matches/", match_controller.MyMatchesView.as_view(), name="my-matches"),
    path(
        "matches/<int:pk>/assign-players/",
        match_controller.MatchAssignPlayersView.as_view(),
        name="assign-players",
    ),
    path(
        "matches/<int:pk>/assign-referee/",
        match_controller.MatchAssignRefereeView.as_view(),
        name="assign-referee",
    ),
    path("matches/<int:pk>/start/", match_controller.MatchStartView.as_view(), name="start-match"),
]
