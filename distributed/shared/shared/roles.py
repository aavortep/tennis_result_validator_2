from django.db import models

class Role(models.TextChoices):
    ORGANIZER = "ORGANIZER", "Organizer"
    REFEREE = "REFEREE", "Referee"
    PLAYER = "PLAYER", "Player"
    SPECTATOR = "SPECTATOR", "Spectator"
