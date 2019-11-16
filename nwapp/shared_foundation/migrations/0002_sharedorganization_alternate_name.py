# Generated by Django 2.2.7 on 2019-11-15 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_foundation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedorganization',
            name='alternate_name',
            field=models.CharField(default=1, help_text='The alternate name this organization.', max_length=63, verbose_name='Alternate Name'),
            preserve_default=False,
        ),
    ]