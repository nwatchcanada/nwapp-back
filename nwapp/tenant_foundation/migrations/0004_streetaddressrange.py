# Generated by Django 2.2.7 on 2020-01-29 03:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant_foundation', '0003_auto_20200129_0344'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreetAddressRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_number_start', models.PositiveSmallIntegerField(help_text='Please select the street number start range.', verbose_name='Street Number Start')),
                ('street_number_end', models.PositiveSmallIntegerField(help_text='Please select the street number end range.', verbose_name='Street Number End')),
                ('street_name', models.CharField(db_index=True, help_text='The name of the street.', max_length=63, unique=True, verbose_name='Street Name')),
                ('street_type', models.PositiveSmallIntegerField(choices=[(2, 'Avenue'), (3, 'Drive'), (4, 'Road'), (5, 'Street'), (6, 'Way'), (1, 'Other')], help_text='Please select the street type.', verbose_name='Street Type')),
                ('street_type_other', models.CharField(blank=True, help_text='Please select the street type not listed in our types.', max_length=127, null=True, verbose_name='Street Type (Other)')),
                ('street_direction', models.PositiveSmallIntegerField(blank=True, choices=[(0, '-'), (1, 'East'), (2, 'North'), (3, 'North East'), (4, 'North West'), (5, 'South'), (6, 'South East'), (7, 'South West'), (8, 'West')], default=0, help_text='Please select the street direction.', verbose_name='Street Direction')),
                ('is_archived', models.BooleanField(blank=True, db_index=True, default=False, help_text='Indicates whether tag was archived.', verbose_name='Is Archived')),
                ('slug', models.SlugField(help_text='The unique identifier used externally.', max_length=255, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('created_from', models.GenericIPAddressField(blank=True, help_text='The IP address of the creator.', null=True, verbose_name='Created from')),
                ('created_from_is_public', models.BooleanField(blank=True, default=False, help_text='Is creator a public IP and is routable.', verbose_name='Is the IP ')),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('last_modified_from', models.GenericIPAddressField(blank=True, help_text='The IP address of the modifier.', null=True, verbose_name='Last modified from')),
                ('last_modified_from_is_public', models.BooleanField(blank=True, default=False, help_text='Is modifier a public IP and is routable.', verbose_name='Is the IP ')),
                ('created_by', models.ForeignKey(blank=True, help_text='The user whom created this object.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_street_address_ranges', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(blank=True, help_text='The user whom modified this object last.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_modified_street_address_ranges', to=settings.AUTH_USER_MODEL)),
                ('watch', models.ForeignKey(help_text='The watch whom this street address range belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='street_address_ranges', to='tenant_foundation.Watch')),
            ],
            options={
                'verbose_name': 'Street Address Range',
                'verbose_name_plural': 'Street Address Ranges',
                'db_table': 'nwapp_street_address_ranges',
                'permissions': (),
                'default_permissions': (),
            },
        ),
    ]