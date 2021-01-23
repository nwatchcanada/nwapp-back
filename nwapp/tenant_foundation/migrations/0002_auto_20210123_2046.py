# Generated by Django 3.0.7 on 2021-01-23 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='facebook_url',
            field=models.URLField(blank=True, default='', help_text='The URL to the Facebook page.', null=True, verbose_name='Facebook URL'),
        ),
        migrations.AddField(
            model_name='watch',
            name='facebook_url',
            field=models.URLField(blank=True, default='', help_text='The URL to the Facebook page.', null=True, verbose_name='Facebook URL'),
        ),
    ]