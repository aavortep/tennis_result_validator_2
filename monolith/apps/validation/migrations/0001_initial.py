import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from shared.utils import evidence_upload_path


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tournaments", "0001_initial"),
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
                        to="results.score",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disputes",
                        to="tournaments.match",
                    ),
                ),
                (
                    "raised_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="raised_disputes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_disputes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "disputes",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Evidence",
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
                    "file",
                    models.FileField(
                        blank=True, null=True, upload_to=evidence_upload_path
                    ),
                ),
                ("description", models.TextField()),
                (
                    "dispute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evidence",
                        to="validation.dispute",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_evidence",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "evidence",
                "db_table": "evidence",
                "ordering": ["-created_at"],
            },
        ),
    ]
