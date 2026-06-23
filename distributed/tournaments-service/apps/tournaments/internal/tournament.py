from django.conf import settings
from django.db import models

from shared.mixins import TimestampMixin


class Tournament(TimestampMixin):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REGISTRATION = "REGISTRATION", "Registration Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    max_players = models.PositiveIntegerField(default=32)
    created_by = models.IntegerField()
    # created_by = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="created_tournaments",
    # )
    # players = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     related_name="tournaments",
    #     blank=True,
    #     limit_choices_to={"role": "PLAYER"},
    # )
    # referees = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     related_name="referee_tournaments",
    #     blank=True,
    #     limit_choices_to={"role": "REFEREE"},
    # )

    class Meta:
        db_table = "tournaments"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name
    
    def get_player_ids(self):
        return list(
            TournamentPlayer.objects.filter(
                tournament=self
            ).values_list(
                "player_id",
                flat=True
            )
        )
    
    def get_referee_ids(self):
        return list(
            TournamentReferee.objects.filter(
                tournament=self
            ).values_list(
                "referee_id",
                flat=True
            )
        )

    @property
    def player_count(self):
        return self.players.count()

    @property
    def is_registration_open(self):
        return self.status == self.Status.REGISTRATION


class TournamentPlayer(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE
    )
    player_id = models.IntegerField()

    class Meta:
        unique_together = (
            "tournament",
            "player_id"
        )


class TournamentReferee(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE
    )
    referee_id = models.IntegerField()

    class Meta:
        unique_together = (
            "tournament",
            "referee_id"
        )
