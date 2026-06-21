from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin
from shared.utils import evidence_upload_path
from .dispute import Dispute


class Evidence(TimestampMixin):
    dispute = models.ForeignKey(
        Dispute, on_delete=models.CASCADE, related_name="evidence"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_evidence",
    )
    file = models.FileField(upload_to=evidence_upload_path, blank=True, null=True)
    description = models.TextField()

    class Meta:
        db_table = "evidence"
        verbose_name_plural = "evidence"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Evidence for dispute #{self.dispute.id} by {self.submitted_by.username}"
        )
