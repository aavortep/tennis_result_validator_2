from django.db import models

from shared.clients.tournaments_service_client import TournamentsServiceClient
from shared.clients.user_service_client import UserServiceClient
from shared.mixins import TimestampMixin


class Ranking(TimestampMixin):
    player = models.IntegerField()
    tournament = models.IntegerField()
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    sets_won = models.IntegerField(default=0)
    sets_lost = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "rankings"
        ordering = ["position", "-points"]
        unique_together = ["player", "tournament"]

    def __str__(self):
        player = UserServiceClient.get_user(self.player)
        tournament = TournamentsServiceClient.get_tournament(self.tournament)
        return f"{player.username} - {tournament.name}: #{self.position}"

    @property
    def matches_played(self):
        return self.wins + self.losses

    @property
    def win_percentage(self):
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100
