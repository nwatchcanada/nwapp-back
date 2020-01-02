# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import (
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)


class Command(BaseCommand):
    help = _('Command will populate tenant specific data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py award_score_point "london" "bart-mika-xyz"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('user_slug', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        slug = options['slug'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Create


        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated tenant content.'))
        )
