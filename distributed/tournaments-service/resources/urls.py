from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.tournaments.web import tournament_views
from apps.matches.web import match_views


urlpatterns = [
    # modules API
    path("api/tournaments/", include("apps.tournaments.api")),
    path("api/matches/", include("apps.matches.api")),

    # tournaments
    path("tournaments/", tournament_views.tournament_list, name="tournament_list"),
    path(
        "tournaments/create/",
        tournament_views.tournament_create,
        name="tournament_create",
    ),
    path(
        "tournaments/<int:pk>/",
        tournament_views.tournament_detail,
        name="tournament_detail",
    ),
    path(
        "tournaments/<int:pk>/edit/",
        tournament_views.tournament_edit,
        name="tournament_edit",
    ),
    path(
        "tournaments/<int:pk>/add-player/",
        tournament_views.tournament_add_player,
        name="tournament_add_player",
    ),
    path(
        "tournaments/<int:pk>/remove-player/<int:player_id>/",
        tournament_views.tournament_remove_player,
        name="tournament_remove_player",
    ),
    path(
        "tournaments/<int:pk>/add-referee/",
        tournament_views.tournament_add_referee,
        name="tournament_add_referee",
    ),
    path("matches/", match_views.my_matches, name="my_matches"),
    path("matches/<int:pk>/", match_views.match_detail, name="match_detail"),
    path(
        "tournaments/<int:tournament_id>/matches/create/",
        match_views.match_create,
        name="match_create",
    ),
    path("matches/<int:pk>/edit/", match_views.match_edit, name="match_edit"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
