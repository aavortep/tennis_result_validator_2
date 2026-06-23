import django.db.models.deletion
from django.db import migrations, models
from shared.utils import evidence_upload_path


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("disputes", "0001_initial"),
    ]

    operations = [
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
                        to="disputes.dispute",
                    ),
                ),
                ("submitted_by", models.IntegerField()),
            ],
            options={
                "verbose_name_plural": "evidence",
                "db_table": "evidence",
                "ordering": ["-created_at"],
            },
        ),
    ]
