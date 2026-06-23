from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import include, path

from apps.rankings.web import ranking_views, global_rankking_views


urlpatterns = [
    # modules API
    path("api/rankings/", include("apps.rankings.api")),

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
