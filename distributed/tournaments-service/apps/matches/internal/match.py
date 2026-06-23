from django.db import models

from shared.mixins import TimestampMixin
from apps.tournaments.internal.tournament import Tournament


class Match(TimestampMixin):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        DISPUTED = "DISPUTED", "Disputed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Round(models.TextChoices):
        ROUND_128 = "R128", "Round of 128"
        ROUND_64 = "R64", "Round of 64"
        ROUND_32 = "R32", "Round of 32"
        ROUND_16 = "R16", "Round of 16"
        QUARTERFINAL = "QF", "Quarterfinal"
        SEMIFINAL = "SF", "Semifinal"
        FINAL = "F", "Final"

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )
    player1_id = models.IntegerField()
    player2_id = models.IntegerField()
    referee_id = models.IntegerField()
    # player1 = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="matches_as_player1",
    # )
    # player2 = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="matches_as_player2",
    # )
    # referee = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="refereed_matches",
    # )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    court = models.CharField(max_length=50, blank=True)
    round = models.CharField(
        max_length=10, choices=Round.choices, default=Round.ROUND_32
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    winner_id = models.IntegerField()
    # winner = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="won_matches",
    # )

    class Meta:
        db_table = "matches"
        ordering = ["scheduled_time"]
        verbose_name_plural = "matches"

    def __str__(self):
        p1 = UserServiceClient.get_user(self.player1_id) if self.player1_id else "TBD"
        p2 = UserServiceClient.get_user(self.player2_id) if self.player2_id else "TBD"
        return f"{self.tournament.name}: player {p1.username} vs player {p2.username} ({self.get_round_display()})"

    @property
    def is_player_assigned(self):
        return self.player1_id is not None and self.player2_id is not None

    def is_player_in_match(self, user):
        return user.id in (self.player1_id, self.player2_id)
