# Generated by Django 2.2.2 on 2020-03-17 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_auto_20200221_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='app',
            field=models.CharField(blank=True, choices=[('general', 'n/a'), ('camp', 'CAMP db'), ('diets', 'Marine diets'), ('esee', 'ESEE (not part of site)'), ('grais', 'grAIS'), ('herring', 'HerMorrhage'), ('ihub', 'iHub'), ('inventory', 'Metadata Inventory'), ('ios2', 'Instruments'), ('masterlist', 'Masterlist'), ('meq', 'Marine environmental quality (MEQ)'), ('oceanography', 'Oceanography'), ('plankton', 'Plankton Net (not part of site)'), ('projects', 'Science project planning'), ('publications', 'Project Publications Inventory'), ('sar_search', 'SAR Search'), ('scifi', 'SciFi'), ('shares', 'Gulf Shares'), ('spot', 'Grants & Contributions (Spot)'), ('spring_cleanup', 'Gulf Region Spring Cleanup'), ('staff', 'Staff Planning Tool'), ('tickets', 'Data Management Tickets'), ('trapnet', 'TrapNet'), ('travel', 'Travel Management System'), ('vault', 'Marine Megafauna Media Vault'), ('whalesdb', 'Whale Equipment Deployment Inventory')], default='general', max_length=25, null=True, verbose_name='application name'),
        ),
    ]
