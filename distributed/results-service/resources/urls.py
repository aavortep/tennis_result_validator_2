from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.scores.web import views as score_views
from apps.disputes.web import dispute_views
from apps.evidence.web import evidence_views


urlpatterns = [
    # modules API
    path("api/scores/", include("apps.scores.api")),
    path("api/disputes/", include("apps.disputes.api")),
    path("api/evidence/", include("apps.evidence.api")),

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
