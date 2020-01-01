# Generated by Django 2.2.7 on 2020-01-01 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0010_auto_20200101_0339'),
    ]

    operations = [
        migrations.AddField(
            model_name='associate',
            name='associate_agreement',
            field=models.TextField(blank=True, help_text='The actual terms of associate agreement the user agreed to when they signed.', null=True, verbose_name='Associate agreement'),
        ),
        migrations.AddField(
            model_name='associate',
            name='associate_agreement_signed_on',
            field=models.DateTimeField(blank=True, help_text='The date when the associate agreement was signed on.', null=True, verbose_name='Associate agreement signed on'),
        ),
        migrations.AddField(
            model_name='associate',
            name='has_signed_associate_agreement',
            field=models.BooleanField(blank=True, default=False, help_text='Boolean indicates whether has agreed to the associate agreement.', verbose_name='Has signed associate agreement'),
        ),
    ]
