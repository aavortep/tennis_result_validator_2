from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.web.roles import Role


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SPECTATOR,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_organizer(self):
        return self.role == Role.ORGANIZER

    @property
    def is_referee(self):
        return self.role == Role.REFEREE

    @property
    def is_player(self):
        return self.role == Role.PLAYER

    @property
    def is_spectator(self):
        return self.role == Role.SPECTATOR
