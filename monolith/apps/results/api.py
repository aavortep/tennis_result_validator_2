from django.urls import path

from .web import score_controller

app_name = "results"

urlpatterns = [
    path("submit/", score_controller.ScoreSubmitView.as_view(), name="score-submit"),
    path("<int:pk>/", score_controller.ScoreDetailView.as_view(), name="score-detail"),
    path("<int:pk>/confirm/", score_controller.ScoreConfirmView.as_view(), name="score-confirm"),
    path("match/<int:match_id>/", score_controller.MatchScoresView.as_view(), name="match-scores"),
]
