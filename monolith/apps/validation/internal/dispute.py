from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin
from apps.results.internal.score import Score


class Dispute(TimestampMixin):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"

    match = models.ForeignKey(
        "tournaments.Match", on_delete=models.CASCADE, related_name="disputes"
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raised_disputes",
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_disputes",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    final_score = models.ForeignKey(
        Score,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispute_resolutions",
    )

    class Meta:
        db_table = "disputes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dispute for {self.match} by {self.raised_by.username}"
