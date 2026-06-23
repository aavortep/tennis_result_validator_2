from django.urls import path

from .web import match_controller

app_name = "matches"

urlpatterns = [
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
