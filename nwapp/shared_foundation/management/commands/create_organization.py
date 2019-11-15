# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from django_rq import get_queue, get_worker
from shared_foundation import constants
from shared_foundation.models import (
    SharedOrganization,
    SharedOrganizationDomain,
    SharedUser
)


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_organization "london" "Over55" "Over55 (London) Inc." "" "CA" "London" "Ontario" "" "N6H 1B4" "78 Riverside Drive" "" "America/Toronto"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('name', nargs='+', type=str)
        parser.add_argument('alternate_name', nargs='+', type=str)
        parser.add_argument('description', nargs='+', type=str)
        parser.add_argument('country', nargs='+', type=str)
        parser.add_argument('locality', nargs='+', type=str)
        parser.add_argument('region', nargs='+', type=str)
        parser.add_argument('timezone_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        name = options['name'][0]
        alternate_name = options['alternate_name'][0]
        description = options['description'][0]
        country = options['country'][0]
        locality = options['locality'][0]
        region = options['region'][0]
        timezone_name = options['timezone_name'][0]

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Check to confirm that we already do not have a `Franchise` with this
        # name in our database.
        organization_does_exist = SharedOrganization.objects.filter(schema_name=schema_name).exists()
        if organization_does_exist:
            raise CommandError(_('Franchise already exists!'))

        # Create our tenant.
        self.begin_processing(schema_name, name, alternate_name, description,
                             country, locality, region, timezone_name)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup organization.'))
        )

    def begin_processing(self, schema_name, name, alternate_name, description,
                         country, locality, region, timezone_name):
        """
        Functin will create a new tenant based on the parameters.
        """

        # Create your tenant
        tenant = SharedOrganization(
            schema_name=schema_name,
            name=name,
            alternate_name=alternate_name,
            description=description,
            country=country,
            locality=locality,
            region=region,
            timezone_name=timezone_name
        )
        tenant.save()

        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705

        # Add one or more domains for the tenant
        domain = SharedOrganizationDomain()
        domain.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN
        domain.domain = tenant.schema_name + '.' + settings.NWAPP_BACKEND_HTTP_DOMAIN
        domain.tenant = tenant
        domain.is_primary = False
        domain.save()

        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705

        # Populate our new organization tenant with post-creation data.
        call_command('populate_tenant_content', schema_name, verbosity=0)
