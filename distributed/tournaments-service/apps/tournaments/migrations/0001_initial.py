import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    # dependencies = [
    #     migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    # ]

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
                    models.IntegerField(),
                ),
            ],
            options={
                "db_table": "tournaments",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="TournamentPlayer",
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
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="players",
                        to="tournaments.tournament",
                    ),
                ),
                (
                    "player_id",
                    models.IntegerField(),
                ),
            ],
            options={
                "db_table": "tournaments_players",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="TournamentReferee",
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
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="referees",
                        to="tournaments.tournament",
                    ),
                ),
                (
                    "referee_id",
                    models.IntegerField(),
                ),
            ],
            options={
                "db_table": "tournaments_referees",
                "ordering": ["-start_date"],
            },
        ),
    ]
