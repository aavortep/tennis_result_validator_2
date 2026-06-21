import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tournaments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ranking",
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
                ("points", models.IntegerField(default=0)),
                ("wins", models.IntegerField(default=0)),
                ("losses", models.IntegerField(default=0)),
                ("sets_won", models.IntegerField(default=0)),
                ("sets_lost", models.IntegerField(default=0)),
                ("games_won", models.IntegerField(default=0)),
                ("games_lost", models.IntegerField(default=0)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rankings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rankings",
                        to="tournaments.tournament",
                    ),
                ),
            ],
            options={
                "db_table": "rankings",
                "ordering": ["position", "-points"],
                "unique_together": {("player", "tournament")},
            },
        ),
        migrations.CreateModel(
            name="GlobalRanking",
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
                ("total_points", models.IntegerField(default=0)),
                ("total_wins", models.IntegerField(default=0)),
                ("total_losses", models.IntegerField(default=0)),
                ("tournaments_played", models.IntegerField(default=0)),
                ("tournaments_won", models.IntegerField(default=0)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "player",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="global_ranking",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "global_rankings",
                "ordering": ["position", "-total_points"],
            },
        ),
    ]
