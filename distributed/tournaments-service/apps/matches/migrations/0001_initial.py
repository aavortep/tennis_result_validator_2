import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tournaments", "0001_initial"),
    ]

    operations = [
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
                    "player1_id",
                    models.IntegerField(),
                ),
                (
                    "player2_id",
                    models.IntegerField(),
                ),
                (
                    "referee_id",
                    models.IntegerField(),
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
                    "winner_id",
                    models.IntegerField(),
                ),
            ],
            options={
                "verbose_name_plural": "matches",
                "db_table": "matches",
                "ordering": ["scheduled_time"],
            },
        ),
    ]
