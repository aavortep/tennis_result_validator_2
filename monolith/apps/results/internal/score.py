from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin


class Score(TimestampMixin):
    match = models.ForeignKey(
        "tournaments.Match", on_delete=models.CASCADE, related_name="scores"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_scores",
    )
    set_scores = models.JSONField(
        help_text='List of set scores: [{"player1": 6, "player2": 4}, ...]'
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="winning_scores",
    )
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_scores",
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "scores"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Score for {self.match} by {self.submitted_by.username}"
