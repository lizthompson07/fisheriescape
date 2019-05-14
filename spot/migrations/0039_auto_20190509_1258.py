# Generated by Django 2.1.4 on 2019-05-09 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0038_auto_20190509_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expressionofinterest',
            name='coordinator_notified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='coordinator was notified'),
        ),
        migrations.AlterField(
            model_name='expressionofinterest',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='expressionofinterest',
            name='feedback',
            field=models.TextField(blank=True, null=True, verbose_name='Feedback to client'),
        ),
        migrations.AlterField(
            model_name='expressionofinterest',
            name='feedback_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='feedback sent to client'),
        ),
        migrations.AlterField(
            model_name='expressionofinterest',
            name='project_eligible',
            field=models.NullBooleanField(verbose_name='is the project eligible?'),
        ),
        migrations.AlterField(
            model_name='expressionofinterest',
            name='title',
            field=models.TextField(blank=True, null=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='final_payment',
            field=models.BooleanField(default=False, verbose_name='Is this a final payment (project-year)?'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='materials_submitted',
            field=models.NullBooleanField(verbose_name='were all necessary materials submitted?'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_confirmed',
            field=models.NullBooleanField(verbose_name='has the payment been confirmed?'),
        ),
        migrations.AlterField(
            model_name='project',
            name='advance_payment',
            field=models.BooleanField(default=True, verbose_name='will this project receive an advance payment?'),
        ),
        migrations.AlterField(
            model_name='project',
            name='advance_payment_sent_to_nhq',
            field=models.DateTimeField(blank=True, null=True, verbose_name='advance payment sent to NHQ'),
        ),
        migrations.AlterField(
            model_name='project',
            name='draft_ca_proponent_approved',
            field=models.DateTimeField(blank=True, null=True, verbose_name='draft CA approved by client'),
        ),
        migrations.AlterField(
            model_name='project',
            name='draft_ca_ready',
            field=models.DateTimeField(blank=True, null=True, verbose_name='draft CA ready'),
        ),
        migrations.AlterField(
            model_name='project',
            name='draft_ca_sent_to_proponent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='draft CA sent to client'),
        ),
        migrations.AlterField(
            model_name='project',
            name='final_ca_nhq_signed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='final CA signed by NHQ'),
        ),
        migrations.AlterField(
            model_name='project',
            name='final_ca_proponent_signed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='final CA signed by client'),
        ),
        migrations.AlterField(
            model_name='project',
            name='final_ca_received',
            field=models.DateTimeField(blank=True, null=True, verbose_name='final CA received from NHQ'),
        ),
        migrations.AlterField(
            model_name='project',
            name='final_ca_sent_to_nhq',
            field=models.DateTimeField(blank=True, null=True, verbose_name='final CA sent to HNQ'),
        ),
        migrations.AlterField(
            model_name='project',
            name='final_ca_sent_to_proponent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='final CA sent to client'),
        ),
        migrations.AlterField(
            model_name='project',
            name='initiation_acknowledgement_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='acknowledgement email sent'),
        ),
        migrations.AlterField(
            model_name='project',
            name='negotiation_letter_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='negotiation letter sent to client'),
        ),
        migrations.AlterField(
            model_name='project',
            name='negotiations_financials_completion_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='negotiation financials complete'),
        ),
        migrations.AlterField(
            model_name='project',
            name='negotiations_workplan_completion_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='negotiation workplan complete'),
        ),
        migrations.AlterField(
            model_name='project',
            name='rank',
            field=models.IntegerField(blank=True, null=True, verbose_name='project rank'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_funding_y1',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended funding amount - Year 1'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_funding_y2',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended funding amount - Year 2'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_funding_y3',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended funding amount - Year 3'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_funding_y4',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended funding amount - Year 4'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_funding_y5',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended funding amount - Year 5'),
        ),
        migrations.AlterField(
            model_name='project',
            name='recommended_overprogramming',
            field=models.FloatField(blank=True, null=True, verbose_name='recommended amount for over-programming'),
        ),
        migrations.AlterField(
            model_name='project',
            name='regional_score',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=18, null=True, verbose_name='regional score'),
        ),
        migrations.AlterField(
            model_name='project',
            name='regrets_or_op_letter_sent_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='client notification sent (OP or Regrets only)'),
        ),
        migrations.AlterField(
            model_name='project',
            name='schedule_5_complete',
            field=models.DateTimeField(blank=True, null=True, verbose_name='schedule_is_complete'),
        ),
        migrations.AlterField(
            model_name='project',
            name='submission_accepted',
            field=models.NullBooleanField(verbose_name='was the submission accepted?'),
        ),
    ]
