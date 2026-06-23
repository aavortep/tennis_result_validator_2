import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    # dependencies = [
    #     ("tournaments", "0001_initial"),
    # ]

    operations = [
        migrations.CreateModel(
            name="Score",
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
                    "set_scores",
                    models.JSONField(
                        help_text='List of set scores: [{"player1": 6, "player2": 4}, ...]'
                    ),
                ),
                ("is_confirmed", models.BooleanField(default=False)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "confirmed_by",
                    models.IntegerField(
                        blank=True,
                        null=True,
                    ),
                ),
                ("match", models.IntegerField()),
                ("submitted_by", models.IntegerField()),
                (
                    "winner",
                    models.IntegerField(
                        blank=True,
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "scores",
                "ordering": ["-created_at"],
            },
        ),
    ]
