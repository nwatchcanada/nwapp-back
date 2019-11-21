# Generated by Django 2.2.7 on 2019-11-21 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0003_auto_20191121_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpectationItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(db_index=True, help_text='The text content of this item.', max_length=127, unique=True, verbose_name='Text')),
                ('sort_number', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0, help_text='The number this item will appear when sorted by number.', verbose_name='Sort #')),
                ('is_for_associate', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the associate.', verbose_name='Is for associate')),
                ('is_for_customer', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the customer.', verbose_name='Is for customer')),
                ('is_for_staff', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the staff.', verbose_name='Is for staff')),
                ('is_for_partner', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the partner.', verbose_name='Is for partner')),
                ('is_archived', models.BooleanField(blank=True, db_index=True, default=False, help_text='Indicates whether how hear item was archived.', verbose_name='Is Archived')),
            ],
            options={
                'verbose_name': 'What do you expect from NW Item',
                'verbose_name_plural': 'What do you expect from NW Items',
                'db_table': 'nwapp_expectation_items',
                'permissions': (),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='MeaningItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(db_index=True, help_text='The text content of this item.', max_length=127, unique=True, verbose_name='Text')),
                ('sort_number', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0, help_text='The number this item will appear when sorted by number.', verbose_name='Sort #')),
                ('is_for_associate', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the associate.', verbose_name='Is for associate')),
                ('is_for_customer', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the customer.', verbose_name='Is for customer')),
                ('is_for_staff', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the staff.', verbose_name='Is for staff')),
                ('is_for_partner', models.BooleanField(blank=True, default=True, help_text='Indicates this option will be visible for the partner.', verbose_name='Is for partner')),
                ('is_archived', models.BooleanField(blank=True, db_index=True, default=False, help_text='Indicates whether how hear item was archived.', verbose_name='Is Archived')),
            ],
            options={
                'verbose_name': 'What does NW mean to you Item',
                'verbose_name_plural': 'What does NW mean to you Items',
                'db_table': 'nwapp_meaning_items',
                'permissions': (),
                'default_permissions': (),
            },
        ),
        migrations.AlterField(
            model_name='member',
            name='how_hear',
            field=models.ForeignKey(blank=True, help_text='How the member heard about the NWApp.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_how_hear_items', to='tenant_foundation.HowHearAboutUsItem'),
        ),
        migrations.AddField(
            model_name='member',
            name='expectation',
            field=models.ForeignKey(blank=True, help_text='What do you expect from NW?', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_expectations', to='tenant_foundation.ExpectationItem'),
        ),
        migrations.AddField(
            model_name='member',
            name='meaning',
            field=models.ForeignKey(blank=True, help_text='What does NW mean to you?', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_meanings', to='tenant_foundation.MeaningItem'),
        ),
    ]
