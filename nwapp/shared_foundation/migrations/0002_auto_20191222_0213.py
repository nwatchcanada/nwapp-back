# Generated by Django 2.2.7 on 2019-12-22 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareduser',
            name='slug',
            field=models.SlugField(help_text='The unique identifier used externally.', max_length=255, unique=True, verbose_name='Slug'),
        ),
    ]
