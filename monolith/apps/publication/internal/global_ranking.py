from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin


class GlobalRanking(TimestampMixin):
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="global_ranking",
    )
    total_points = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    tournaments_played = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "global_rankings"
        ordering = ["position", "-total_points"]

    def __str__(self):
        return f"{self.player.username}: Global #{self.position}"
