import csv
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import (
    Watch
)


class Command(BaseCommand):
    help = _('Command will load up historical data for tenant with the "watches.csv" file.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py import_watches_from_csv "london" "/Users/bmika/python/github.com/nwatchcanada/nwapp-data/watches.csv""
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('full_filepath', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Get the user inputs.
        schema_name = options['schema_name'][0]
        full_filepath = options['full_filepath'][0]

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Importing `Watches` at path: %(url)s ...') % {
                'url': full_filepath
            })
        )

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Begin importing...
        with open(full_filepath, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i, row_dict in enumerate(csvreader):
                if i > 0:
                    # Begin importing...
                    self.run_import_from_dict(row_dict, i)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated tenant content.'))
        )

    def run_import_from_dict(self, row_dict, index):
        watch_id = row_dict[0]
        name = row_dict[1]
        street_number_start = row_dict[2]
        street_number_end = row_dict[3]
        street_name = row_dict[4]
        street_type = row_dict[5]
        street_direction = row_dict[6]
        apt_number_start = row_dict[7]
        apt_number_end = row_dict[8]
        range_type = row_dict[9]
        print("Watch ID:", watch_id)
        print("Watch Name:", name)
        print("Street # Start:", street_number_start)
        print("Street # End:", street_number_end)
        print("Street Name:", street_name)
        print("Street Type:", street_type)
        print("Street Direction:", street_direction)
        print("Apartment # Start:", apt_number_start)
        print("Apartment # End:", apt_number_end)
        print("Range Type:", range_type)
        print("\n")
