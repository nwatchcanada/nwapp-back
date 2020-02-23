# Generated by Django 2.2.7 on 2020-02-23 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0002_auto_20200222_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='date',
            field=models.DateTimeField(blank=True, help_text='The date this event occured.', null=True, verbose_name='Date'),
        ),
        migrations.AddField(
            model_name='item',
            name='has_accept_authority_cooperation',
            field=models.BooleanField(blank=True, default=False, help_text='Has user agreed to the fact that NW can contact the local and federal police services?', verbose_name='Has accepted authority cooperation'),
        ),
        migrations.AddField(
            model_name='item',
            name='has_notified_authorities',
            field=models.BooleanField(blank=True, default=False, help_text='Has notified authorities?', verbose_name='Has notified authorities'),
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.CharField(blank=True, default='', help_text='The location of where this event occured.', max_length=127, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='item',
            name='state',
            field=models.CharField(blank=True, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('archived', 'Archived')], db_index=True, default='active', help_text='The state of this item.', max_length=15, verbose_name='State'),
        ),
    ]