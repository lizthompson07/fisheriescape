# Generated by Django 4.1.6 on 2023-02-22 18:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("shared_models", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("valid_from", models.DateTimeField()),
                ("valid_to", models.DateTimeField()),
                ("subject_en", models.CharField(max_length=150)),
                ("subject_fr", models.CharField(blank=True, max_length=150, null=True)),
                ("message_en", models.TextField()),
                ("message_fr", models.TextField(blank=True, null=True)),
                (
                    "alert_type",
                    models.CharField(
                        choices=[
                            ("alert-primary", "primary (blue"),
                            ("alert-secondary", "secondary (light grey)"),
                            ("alert-success", "success (green)"),
                            ("alert-danger", "danger (red)"),
                            ("alert-warning", "warning (yellow)"),
                            ("alert-info", "info (teal)"),
                            ("alert-light", "light (white)"),
                            ("alert-dark", "dark (dark grey)"),
                        ],
                        default="primary",
                        max_length=25,
                    ),
                ),
            ],
            options={
                "ordering": ["-valid_from"],
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position_eng",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="position (English)",
                    ),
                ),
                (
                    "position_fre",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="position (French)",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="phone (office)",
                    ),
                ),
                ("retired", models.BooleanField(default=False)),
                (
                    "language",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="shared_models.language",
                        verbose_name="language preference",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="shared_models.section",
                        verbose_name="Section",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["user__first_name", "user__last_name"],
            },
        ),
    ]
