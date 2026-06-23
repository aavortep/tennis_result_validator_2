from django.db import models

from shared.clients.user_service_client import UserServiceClient
from shared.mixins import TimestampMixin
from shared.utils import evidence_upload_path
from apps.disputes.internal.dispute import Dispute


class Evidence(TimestampMixin):
    dispute = models.ForeignKey(
        Dispute, on_delete=models.CASCADE, related_name="evidence"
    )
    submitted_by = models.IntegerField()
    file = models.FileField(upload_to=evidence_upload_path, blank=True, null=True)
    description = models.TextField()

    class Meta:
        db_table = "evidence"
        verbose_name_plural = "evidence"
        ordering = ["-created_at"]

    def __str__(self):
        submitted_by = UserServiceClient.get_user(self.submitted_by)
        return (
            f"Evidence for dispute #{self.dispute.id} by {submitted_by.username}"
        )
