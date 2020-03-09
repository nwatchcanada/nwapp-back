# Generated by Django 2.2.7 on 2020-03-09 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0013_auto_20200309_0043'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskitem',
            name='staff',
            field=models.ForeignKey(blank=True, help_text='The staff member which is responsibel for processing this task item.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_items', to='tenant_foundation.Staff'),
        ),
        migrations.AlterField(
            model_name='taskitem',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Unassigned'), (2, 'Pending'), (3, 'Closed')], db_index=True, help_text='The state of task item.', verbose_name='State'),
        ),
    ]
