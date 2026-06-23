from django.db import models

from shared.clients.user_service_client import UserServiceClient
from shared.mixins import TimestampMixin


class GlobalRanking(TimestampMixin):
    player = models.IntegerField()
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
        player = UserServiceClient.get_user(self.player)
        return f"{player.username}: Global #{self.position}"
