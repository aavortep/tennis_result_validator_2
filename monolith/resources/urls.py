from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import include, path

from apps.users.web import views as accounts_views
from apps.tournaments.web import tournament_views, match_views
from apps.results.web import views as score_views
from apps.validation.web import dispute_views, evidence_views
from apps.publication.web import ranking_views, global_rankking_views


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),

    # modules API
    path("api/accounts/", include("apps.users.api")),
    path("api/tournaments/", include("apps.tournaments.api")),
    path("api/scores/", include("apps.results.api")),
    path("api/validation/", include("apps.validation.api")),
    path("api/rankings/", include("apps.publication.api")),

    # users
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),
    path("register/", accounts_views.register_view, name="register"),
    path("profile/", accounts_views.profile_view, name="profile"),

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

    # scores
    path(
        "matches/<int:match_id>/score/", score_views.score_submit, name="score_submit"
    ),
    path("scores/<int:pk>/confirm/", score_views.score_confirm, name="score_confirm"),

    # validation
    path("disputes/", dispute_views.dispute_list, name="dispute_list"),
    path("disputes/<int:pk>/", dispute_views.dispute_detail, name="dispute_detail"),
    path(
        "matches/<int:match_id>/dispute/",
        dispute_views.dispute_create,
        name="dispute_create",
    ),
    path(
        "disputes/<int:pk>/resolve/",
        dispute_views.dispute_resolve,
        name="dispute_resolve",
    ),
    path(
        "disputes/<int:dispute_id>/evidence/",
        evidence_views.evidence_add,
        name="evidence_add",
    ),

    # publication
    path("rankings/", global_rankking_views.global_rankings, name="global_rankings"),
    path(
        "rankings/tournament/<int:tournament_id>/",
        ranking_views.tournament_rankings,
        name="tournament_rankings",
    ),
    path("rankings/my/", ranking_views.my_rankings, name="my_rankings"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
