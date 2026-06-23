from django.urls import path

from .web import ranking_controller, global_ranking_controller

app_name = "rankings"

urlpatterns = [
    path(
        "tournament/<int:tournament_id>/",
        ranking_controller.TournamentLeaderboardView.as_view(),
        name="tournament-leaderboard",
    ),
    path("global/", global_ranking_controller.GlobalLeaderboardView.as_view(), name="global-leaderboard"),
    path("my/", ranking_controller.MyRankingsView.as_view(), name="my-rankings"),
    path("my/global/", global_ranking_controller.MyGlobalRankingView.as_view(), name="my-global-ranking"),
    path(
        "player/<int:player_id>/",
        ranking_controller.PlayerRankingsView.as_view(),
        name="player-rankings",
    ),
    path("<int:pk>/", ranking_controller.RankingDetailView.as_view(), name="ranking-detail"),
    path(
        "tournament/<int:tournament_id>/initialize/",
        ranking_controller.InitializeTournamentRankingsView.as_view(),
        name="initialize-rankings",
    ),
    path(
        "tournament/<int:tournament_id>/recalculate/",
        ranking_controller.RecalculateRankingsView.as_view(),
        name="recalculate-rankings",
    ),
    path(
        "head-to-head/<int:player1_id>/<int:player2_id>/",
        ranking_controller.HeadToHeadView.as_view(),
        name="head-to-head",
    ),
]
