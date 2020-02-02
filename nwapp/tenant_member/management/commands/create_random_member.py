# -*- coding: utf-8 -*-
from freezegun import freeze_time
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.model_resources import seed_members
from tenant_member.tasks import process_member_with_slug_func


class Command(BaseCommand):
    help = _('Command will generate random members.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_random_member "london" 1
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('length', nargs='+', type=int)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Get the user inputs.
        schema_name = options['schema_name'][0]
        length = options['length'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        members = seed_members(organization, length)

        # Iterate through all the randomly generated members
        for member in members:
            freezer = freeze_time(member.last_modified_at)
            freezer.start()

            # Run the following which will save our searchable content.
            member.indexed_text = Member.get_searchable_content(member)
            member.save()

            freezer.stop()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully seed the following member(s):'))
        )

        for member in members:
            self.stdout.write(
                self.style.SUCCESS(_('Slug %(slug)s.') %{
                    'slug': member.user.slug,
                })
            )
