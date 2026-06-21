from django.urls import path

from .web import dispute_controller, evidence_controller

app_name = "validation"

urlpatterns = [
    path("disputes/", dispute_controller.DisputeListView.as_view(), name="dispute-list"),
    path("disputes/open/", dispute_controller.OpenDisputesView.as_view(), name="open-disputes"),
    path("disputes/create/", dispute_controller.DisputeCreateView.as_view(), name="dispute-create"),
    path(
        "disputes/<int:pk>/", dispute_controller.DisputeDetailView.as_view(), name="dispute-detail"
    ),
    path(
        "disputes/<int:pk>/resolve/",
        dispute_controller.DisputeResolveView.as_view(),
        name="dispute-resolve",
    ),
    path(
        "disputes/<int:pk>/review/",
        dispute_controller.DisputeReviewView.as_view(),
        name="dispute-review",
    ),
    path(
        "disputes/<int:pk>/evidence/",
        evidence_controller.DisputeEvidenceView.as_view(),
        name="dispute-evidence",
    ),
    path(
        "evidence/submit/", evidence_controller.EvidenceCreateView.as_view(), name="evidence-submit"
    ),
]
