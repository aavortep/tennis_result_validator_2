from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin
from shared.clients.user_service_client import UserServiceClient


class Score(TimestampMixin):
    match = models.IntegerField()
    submitted_by = models.IntegerField()
    set_scores = models.JSONField(
        help_text='List of set scores: [{"player1": 6, "player2": 4}, ...]'
    )
    winner = models.IntegerField(
        null=True,
        blank=True,
    )
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.IntegerField(
        null=True,
        blank=True,
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "scores"
        ordering = ["-created_at"]

    def __str__(self):
        submitted_by_user = UserServiceClient.get_user(self.submitted_by)
        return f"Score for match {self.match} by {submitted_by_user.username}"
