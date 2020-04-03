# Generated by Django 3.0.4 on 2020-04-03 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0002_auto_20200403_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unifiedsearchitem',
            name='type_of',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Customer'), (2, 'Area Coordinator'), (3, 'Associate'), (4, 'Staff'), (5, 'Item'), (6, 'Watch'), (7, 'District'), (8, 'File')], db_index=True, help_text='The type of item this is.', verbose_name='Type of'),
        ),
    ]