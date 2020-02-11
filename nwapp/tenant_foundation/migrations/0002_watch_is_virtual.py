# Generated by Django 2.2.7 on 2020-02-11 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='watch',
            name='is_virtual',
            field=models.BooleanField(blank=True, db_index=True, default=False, help_text='Indicates whether watch is a virtual watch.', verbose_name='Is Virtual Watch'),
        ),
    ]