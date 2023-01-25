# Generated by Django 3.2.16 on 2023-01-23 17:45
import datetime
from django.utils import timezone

from django.db import migrations


# code largely based from: https://docs.djangoproject.com/en/4.1/howto/writing-migrations/
def set_init_sample_batches(apps, schema_editor):
    Sample = apps.get_model('edna', 'Sample')
    SampleBatch = apps.get_model('edna', 'SampleBatch')

    for sample_obj in Sample.objects.all():
        if not sample_obj.sample_batch:
            sample_batch_obj = SampleBatch.objects.filter(default_collection=sample_obj.collection).first()
            if not sample_batch_obj:
                sample_batch_obj = SampleBatch.objects.create(
                    default_collection=sample_obj.collection,
                    datetime=timezone.now()
                )
            sample_obj.sample_batch = sample_batch_obj
            sample_obj.save(update_fields=['sample_batch'])


class Migration(migrations.Migration):

    dependencies = [
        ('edna', '0004_auto_20230123_1345'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(set_init_sample_batches, reverse_code=migrations.RunPython.noop),
    ]
