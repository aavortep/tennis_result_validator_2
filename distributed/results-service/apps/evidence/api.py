from django.urls import path

from .web import evidence_controller

app_name = "evidence"

urlpatterns = [
    path(
        "disputes/<int:pk>/evidence/",
        evidence_controller.DisputeEvidenceView.as_view(),
        name="dispute-evidence",
    ),
    path(
        "evidence/submit/", evidence_controller.EvidenceCreateView.as_view(), name="evidence-submit"
    ),
]
