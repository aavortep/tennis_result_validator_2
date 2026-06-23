import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("scores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dispute",
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
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("OPEN", "Open"),
                            ("UNDER_REVIEW", "Under Review"),
                            ("RESOLVED", "Resolved"),
                        ],
                        default="OPEN",
                        max_length=20,
                    ),
                ),
                ("resolution_notes", models.TextField(blank=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "final_score",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="dispute_resolutions",
                        to="scores.score",
                    ),
                ),
                ("match", models.IntegerField()),
                ("raised_by", models.IntegerField()),
                (
                    "resolved_by",
                    models.IntegerField(
                        blank=True,
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "disputes",
                "ordering": ["-created_at"],
            },
        ),
    ]
