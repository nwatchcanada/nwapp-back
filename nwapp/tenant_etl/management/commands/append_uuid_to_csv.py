# -*- coding: utf-8 -*-
import csv
import os
import sys
import re
import uuid
import os.path as ospath
import codecs
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedOrganization
from tenant_foundation.models import District


"""
Run manually in console:
python manage.py append_uuid_to_csv "london" "/Users/bmika/python/github.com/nwatchcanada/nwapp-back/nwapp/tenant_etl/csv/prod_districts.csv"
"""


class Command(BaseCommand):
    help = _('Command will load up historical data for area coordinators.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('full_filepath', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        full_filepath = options['full_filepath'][0]

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Importing `Test` at path: %(url)s ...') % {
                'url': full_filepath
            })
        )

        try:
            tenant = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        raw_data = open(full_filepath, encoding='utf-8')

        processed_content = []

        with open(full_filepath, newline='') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                new_row = self.process_content(tenant, row)
                processed_content.append(new_row)

        raw_data.close()

        print(processed_content)


        edited_full_filepath = full_filepath.replace(".csv", "_plus_uuid.csv")
        with open(edited_full_filepath, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            for content in processed_content:
                print(content)
                spamwriter.writerow(content)


        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully appended.'))
        )

    def process_content(self, tenant, row):
        uuid_obj = uuid.uuid4()
        uuid_str = str(uuid_obj)
        row.append(uuid_str)
        return row
