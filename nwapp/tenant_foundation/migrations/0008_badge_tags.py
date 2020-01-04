# Generated by Django 2.2.7 on 2020-01-04 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0007_auto_20200104_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='The tags associated with this badge.', related_name='badges', to='tenant_foundation.Tag'),
        ),
    ]
