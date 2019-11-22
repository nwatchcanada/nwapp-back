# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import (
    Tag
)


class Command(BaseCommand):
    help = _('Command will populate tenant specific data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py populate_tenant_content "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Update content.
        self.populate_default_tags(organization)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated tenant content.'))
        )

    def populate_default_tags(self, tenant):
        Tag.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'text': 'Security',
                'description': 'Please use this tag if something is related to security.',
                'is_archived': False,
            }
        )
        Tag.objects.update_or_create(
            id=2,
            defaults={
                'id': 2,
                'text': 'Blacklist',
                'description': 'Please use this tag if someone is blacklisted from our system.',
                'is_archived': False,
            }
        )
        Tag.objects.update_or_create(
            id=3,
            defaults={
                'id': 3,
                'text': 'Residential',
                'description': 'Tag pertaining to residential items in our system.',
                'is_archived': False,
            }
        )
        Tag.objects.update_or_create(
            id=4,
            defaults={
                'id': 4,
                'text': 'Commercial',
                'description': 'Tag pertaining to commercial items in our system.',
                'is_archived': False,
            }
        )
