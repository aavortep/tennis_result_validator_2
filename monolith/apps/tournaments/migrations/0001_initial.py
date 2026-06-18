import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tournament",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("location", models.CharField(max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("REGISTRATION", "Registration Open"),
                            ("IN_PROGRESS", "In Progress"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="DRAFT",
                        max_length=20,
                    ),
                ),
                ("max_players", models.PositiveIntegerField(default=32)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_tournaments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "players",
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={"role": "PLAYER"},
                        related_name="tournaments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "referees",
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={"role": "REFEREE"},
                        related_name="referee_tournaments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "tournaments",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("scheduled_time", models.DateTimeField(blank=True, null=True)),
                ("court", models.CharField(blank=True, max_length=50)),
                (
                    "round",
                    models.CharField(
                        choices=[
                            ("R128", "Round of 128"),
                            ("R64", "Round of 64"),
                            ("R32", "Round of 32"),
                            ("R16", "Round of 16"),
                            ("QF", "Quarterfinal"),
                            ("SF", "Semifinal"),
                            ("F", "Final"),
                        ],
                        default="R32",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SCHEDULED", "Scheduled"),
                            ("IN_PROGRESS", "In Progress"),
                            ("COMPLETED", "Completed"),
                            ("DISPUTED", "Disputed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="SCHEDULED",
                        max_length=20,
                    ),
                ),
                (
                    "player1",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="matches_as_player1",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "player2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="matches_as_player2",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "referee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="refereed_matches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="matches",
                        to="tournaments.tournament",
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="won_matches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "matches",
                "db_table": "matches",
                "ordering": ["scheduled_time"],
            },
        ),
    ]
