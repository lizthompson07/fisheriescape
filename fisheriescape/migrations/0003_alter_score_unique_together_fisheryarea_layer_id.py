# Generated by Django 4.1.6 on 2023-03-01 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fisheriescape", "0002_hexagon_grid_id_species_english_name_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="score",
            unique_together={("hexagon", "week")},
        ),
        migrations.AddIndex(
            model_name="fisheryarea",
            index=models.Index(["layer_id"], name="layer_id"),
        ),
    ]
