# Generated by Django 4.1.6 on 2023-02-22 18:05

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import fisheriescape.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Hexagon",
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
                    "grid_id",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        unique=True,
                        verbose_name="grid id",
                    ),
                ),
                (
                    "polygon",
                    django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MarineMammal",
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
                    "english_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="english name",
                    ),
                ),
                (
                    "english_name_short",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="short english name",
                    ),
                ),
                (
                    "french_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="french name",
                    ),
                ),
                (
                    "french_name_short",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="short french name",
                    ),
                ),
                (
                    "latin_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="scientific name",
                    ),
                ),
                (
                    "population",
                    models.CharField(
                        blank=True, max_length=250, null=True, verbose_name="population"
                    ),
                ),
                (
                    "sara_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("No Status", "No Status"),
                            ("Not at Risk", "Not at Risk"),
                            ("Special Concern", "Special Concern"),
                            ("Threatened", "Threatened"),
                            ("Endangered", "Endangered"),
                            ("Extirpated", "Extirpated"),
                            ("Extinct", "Extinct"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="sara status",
                    ),
                ),
                (
                    "cosewic_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("No Status", "No Status"),
                            ("Not at Risk", "Not at Risk"),
                            ("Special Concern", "Special Concern"),
                            ("Threatened", "Threatened"),
                            ("Endangered", "Endangered"),
                            ("Extirpated", "Extirpated"),
                            ("Extinct", "Extinct"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="cosewic assessed",
                    ),
                ),
                (
                    "website",
                    models.URLField(
                        blank=True, max_length=250, null=True, verbose_name="website"
                    ),
                ),
            ],
            options={
                "ordering": ["english_name"],
            },
        ),
        migrations.CreateModel(
            name="Mitigation",
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
                    "mitigation_type",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="mitigation type",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="description",
                    ),
                ),
            ],
            options={
                "ordering": ["mitigation_type"],
            },
        ),
        migrations.CreateModel(
            name="Species",
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
                    "english_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="english name",
                    ),
                ),
                (
                    "french_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="french name",
                    ),
                ),
                (
                    "latin_name",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="scientific name",
                    ),
                ),
                (
                    "website",
                    models.CharField(
                        blank=True, max_length=250, null=True, verbose_name="website"
                    ),
                ),
            ],
            options={
                "ordering": ["english_name"],
            },
        ),
        migrations.CreateModel(
            name="Week",
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
                    "week_number",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MaxValueValidator(53),
                            django.core.validators.MinValueValidator(1),
                        ],
                        verbose_name="week",
                    ),
                ),
                (
                    "approx_start",
                    models.DateField(
                        blank=True, null=True, verbose_name="approx start"
                    ),
                ),
                (
                    "approx_end",
                    models.DateField(blank=True, null=True, verbose_name="approx end"),
                ),
            ],
            options={
                "ordering": ["week_number"],
            },
        ),
        migrations.CreateModel(
            name="Score",
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
                    "site_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=10,
                        null=True,
                        verbose_name="site score",
                    ),
                ),
                (
                    "ceu_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=4,
                        max_digits=10,
                        null=True,
                        verbose_name="ceu score",
                    ),
                ),
                (
                    "fs_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=4,
                        max_digits=8,
                        null=True,
                        verbose_name="fs score",
                    ),
                ),
                (
                    "hexagon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="scores",
                        to="fisheriescape.hexagon",
                        verbose_name="hexagon",
                    ),
                ),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="scores",
                        to="fisheriescape.species",
                        verbose_name="species",
                    ),
                ),
                (
                    "week",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="scores",
                        to="fisheriescape.week",
                        verbose_name="week",
                    ),
                ),
            ],
            options={
                "ordering": ["species", "week"],
            },
        ),
        migrations.CreateModel(
            name="NAFOArea",
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
                    "layer_id",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="layer id"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="nafo area name",
                    ),
                ),
                (
                    "polygon",
                    django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326),
                ),
            ],
            options={
                "ordering": ["name"],
                "unique_together": {("name", "layer_id")},
            },
        ),
        migrations.CreateModel(
            name="FisheryArea",
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
                    "layer_id",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="layer id"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="fisheries area name",
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Gulf", "Gulf"),
                            ("Mar", "Maritimes"),
                            ("NL", "Newfoundland"),
                            ("QC", "Quebec"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="DFO region",
                    ),
                ),
                (
                    "polygon",
                    django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326),
                ),
                (
                    "nafo_area",
                    models.ManyToManyField(
                        blank=True,
                        related_name="nafoareas",
                        to="fisheriescape.nafoarea",
                        verbose_name="nafo area name",
                    ),
                ),
            ],
            options={
                "ordering": ["layer_id", "name"],
            },
        ),
        migrations.CreateModel(
            name="Fishery",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "participants",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="participants"
                    ),
                ),
                (
                    "participant_detail",
                    models.TextField(
                        blank=True, null=True, verbose_name="participant detail"
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="start date of season"
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="end date of season"
                    ),
                ),
                (
                    "fishery_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Active", "Active"),
                            ("Experimental", "Experimental"),
                            ("Inactive", "Inactive"),
                            ("Unknown", "Unknown"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="fishery status",
                    ),
                ),
                (
                    "license_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Multi", "Multi Species"),
                            ("Single", "Single Species"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="type of license",
                    ),
                ),
                (
                    "management_system",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Effort Control", "Effort Control"),
                            ("Quota - Competitive", "Quota - Competitive"),
                            ("Quota - Individual", "Quota - Individual"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="management system",
                    ),
                ),
                (
                    "fishery_comment",
                    models.TextField(
                        blank=True, null=True, verbose_name="general comments"
                    ),
                ),
                (
                    "gear_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Gillnets", "Gillnets"),
                            ("Longlines", "Longlines"),
                            ("Pots / Traps", "Pots / Traps"),
                            ("Set Gillnet", "Set Gillnet"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="gear type",
                    ),
                ),
                (
                    "gear_amount",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="avg gear amount per participant",
                    ),
                ),
                (
                    "gear_config",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="gear configuration",
                    ),
                ),
                (
                    "gear_soak",
                    models.FloatField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="avg rope soak time",
                    ),
                ),
                (
                    "gear_primary_colour",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("Blue", "Blue"),
                            ("Black", "Black"),
                            ("Red", "Red"),
                            ("Yellow", "Yellow"),
                            ("White", "White"),
                            ("Purple", "Purple"),
                            ("Orange", "Orange"),
                            ("Green", "Green"),
                            ("Grey", "Grey"),
                            ("Brown", "Brown"),
                            ("Pink", "Pink"),
                            ("Red/White Pattern", "Red/White Pattern"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="gear primary colour",
                    ),
                ),
                (
                    "gear_secondary_colour",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("Blue", "Blue"),
                            ("Black", "Black"),
                            ("Red", "Red"),
                            ("Yellow", "Yellow"),
                            ("White", "White"),
                            ("Purple", "Purple"),
                            ("Orange", "Orange"),
                            ("Green", "Green"),
                            ("Grey", "Grey"),
                            ("Brown", "Brown"),
                            ("Pink", "Pink"),
                            ("Red/White Pattern", "Red/White Pattern"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="gear secondary colour",
                    ),
                ),
                (
                    "gear_tertiary_colour",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("Blue", "Blue"),
                            ("Black", "Black"),
                            ("Red", "Red"),
                            ("Yellow", "Yellow"),
                            ("White", "White"),
                            ("Purple", "Purple"),
                            ("Orange", "Orange"),
                            ("Green", "Green"),
                            ("Grey", "Grey"),
                            ("Brown", "Brown"),
                            ("Pink", "Pink"),
                            ("Red/White Pattern", "Red/White Pattern"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="gear tertiary colour",
                    ),
                ),
                (
                    "gear_comment",
                    models.TextField(
                        blank=True, null=True, verbose_name="gear comments"
                    ),
                ),
                (
                    "monitoring_aso",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="at sea observer (ASO)",
                    ),
                ),
                (
                    "monitoring_dockside",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="dockside monitoring",
                    ),
                ),
                (
                    "monitoring_logbook",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="logbook",
                    ),
                ),
                (
                    "monitoring_vms",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="vessel monitoring system (VMS)",
                    ),
                ),
                (
                    "monitoring_comment",
                    models.TextField(
                        blank=True, null=True, verbose_name="monitoring comments"
                    ),
                ),
                (
                    "mitigation_comment",
                    models.TextField(
                        blank=True, null=True, verbose_name="mitigation comments"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fishery_areas",
                    models.ManyToManyField(
                        related_name="fisherys",
                        to="fisheriescape.fisheryarea",
                        verbose_name="fishery areas",
                    ),
                ),
                (
                    "marine_mammals",
                    models.ManyToManyField(
                        blank=True,
                        related_name="fisherys",
                        to="fisheriescape.marinemammal",
                        verbose_name="marine mammals",
                    ),
                ),
                (
                    "mitigation",
                    models.ManyToManyField(
                        blank=True,
                        related_name="fisherys",
                        to="fisheriescape.mitigation",
                        verbose_name="mitigation type",
                    ),
                ),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="fisherys",
                        to="fisheriescape.species",
                        verbose_name="species",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["start_date", "species"],
            },
        ),
        migrations.CreateModel(
            name="Analyses",
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
                    "type",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Common Unit Effort"),
                            (2, "Site Score"),
                            (3, "Fisheriescape Index"),
                        ],
                        null=True,
                        verbose_name="type",
                    ),
                ),
                (
                    "ref_text",
                    models.TextField(
                        blank=True, null=True, verbose_name="reference text"
                    ),
                ),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="analysess",
                        to="fisheriescape.species",
                        verbose_name="species",
                    ),
                ),
                (
                    "week",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="weeks",
                        to="fisheriescape.week",
                        verbose_name="week",
                    ),
                ),
            ],
            options={
                "ordering": ["week", "species"],
            },
        ),
        migrations.AddIndex(
            model_name="score",
            index=models.Index(["species", "week"], name="species_week"),
        ),
        migrations.AddIndex(
            model_name="score",
            index=models.Index(["week"], name="week"),
        ),
        migrations.AddIndex(
            model_name="score",
            index=models.Index(["species"], name="species"),
        ),
        migrations.AlterUniqueTogether(
            name="fisheryarea",
            unique_together={("name", "layer_id")},
        ),
    ]
