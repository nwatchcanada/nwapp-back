# Generated by Django 2.2.7 on 2019-11-21 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant_foundation', '0004_auto_20191121_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='expectation',
        ),
        migrations.RemoveField(
            model_name='member',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='member',
            name='how_hear',
        ),
        migrations.RemoveField(
            model_name='member',
            name='meaning',
        ),
        migrations.RemoveField(
            model_name='member',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='member',
            name='year_of_birth',
        ),
        migrations.CreateModel(
            name='MemberMetric',
            fields=[
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='tenant_foundation.Member')),
                ('how_hear_other', models.CharField(blank=True, default='Did not answer', help_text='How member heared/learned about this NWApp.', max_length=2055, verbose_name='Learned about us (other)')),
                ('expectation_other', models.CharField(blank=True, default='Did not answer', help_text='-', max_length=2055, verbose_name='What do you expect from NW? (other)')),
                ('meaning_other', models.CharField(blank=True, default='Did not answer', help_text='-', max_length=2055, verbose_name='What does NW mean to you? (other)')),
                ('volunteer', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Yes'), (0, 'No'), (2, 'Maybe')], default=2, help_text='Are you willing to volunteer as a area coordinator / associate', verbose_name='Willing to volunteer?')),
                ('gender', models.CharField(blank=True, help_text='Gender of the person. While `Male` and `Female` may be used, text strings are also acceptable for people who do not identify as a binary gender.', max_length=31, null=True, verbose_name='Gender')),
                ('year_of_birth', models.PositiveSmallIntegerField(blank=True, default=0, help_text='The year that this member was born in.', verbose_name='Year of Birth')),
                ('created_from', models.GenericIPAddressField(blank=True, help_text='The IP address of the creator.', null=True, verbose_name='Created from')),
                ('created_from_is_public', models.BooleanField(blank=True, default=False, help_text='Is creator a public IP and is routable.', verbose_name='Is the IP ')),
                ('last_modified_from', models.GenericIPAddressField(blank=True, help_text='The IP address of the modifier.', null=True, verbose_name='Last modified from')),
                ('last_modified_from_is_public', models.BooleanField(blank=True, default=False, help_text='Is modifier a public IP and is routable.', verbose_name='Is the IP ')),
                ('created_by', models.ForeignKey(blank=True, help_text='The user whom created this object.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_member_metrics', to=settings.AUTH_USER_MODEL)),
                ('expectation', models.ForeignKey(blank=True, help_text='What do you expect from NW?', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_metric_expectations', to='tenant_foundation.ExpectationItem')),
                ('how_hear', models.ForeignKey(blank=True, help_text='How the member heard about the NWApp.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_metric_how_hear_items', to='tenant_foundation.HowHearAboutUsItem')),
                ('last_modified_by', models.ForeignKey(blank=True, help_text='The user whom modified this object last.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_modified_member_metrics', to=settings.AUTH_USER_MODEL)),
                ('meaning', models.ForeignKey(blank=True, help_text='What does NW mean to you?', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_metric_meanings', to='tenant_foundation.MeaningItem')),
                ('tags', models.ManyToManyField(blank=True, help_text='The tags associated with this member.', related_name='member_metric_tags', to='tenant_foundation.Tag')),
            ],
            options={
                'verbose_name': 'Member Metric',
                'verbose_name_plural': 'Members Metrics',
                'db_table': 'nwapp_member_metrics',
                'permissions': (),
                'default_permissions': (),
            },
        ),
    ]
