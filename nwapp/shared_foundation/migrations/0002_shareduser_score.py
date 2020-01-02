# Generated by Django 2.2.7 on 2020-01-02 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareduser',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, default=0, help_text='The total score accumulated currently.', verbose_name='Score'),
        ),
    ]
