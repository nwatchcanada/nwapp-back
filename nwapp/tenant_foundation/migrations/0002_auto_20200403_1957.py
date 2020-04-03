# Generated by Django 3.0.4 on 2020-04-03 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unifiedsearchitem',
            name='type_of',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Customer'), (3, 'Area Coordinator'), (2, 'Associate'), (4, 'Staff'), (5, 'Item'), (6, 'Watch'), (7, 'District'), (8, 'File')], db_index=True, help_text='The type of item this is.', verbose_name='Type of'),
        ),
    ]