# -*- coding: utf-8 -*-
from freezegun import freeze_time
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import AreaCoordinator, Member


class Command(BaseCommand):
    help = _('Command will generate random area coordinators.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_random_area_coordinator "london" 1
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

        members = Member.seed(organization, length)

        # Iterate through all the randomly generated members
        for member in members:
            freezer = freeze_time(member.last_modified_at)
            freezer.start()

            # Run the following which will save our searchable content.
            indexed_text = Member.get_searchable_content(member)
            member.indexed_text = Truncator(indexed_text).chars(1023)
            member.save()

            # Promote the `member` to be an `area coordinator`.
            area_coordinator = member.promote_to_area_coordinator(defaults={
                'has_signed_area_coordinator_agreement': True,
                'has_signed_conflict_of_interest_agreement': True,
                'has_signed_code_of_conduct_agreement': True,
                'has_signed_confidentiality_agreement': True,
                'police_check_date': None,
                'created_by': None,
                'created_from': None,
                'created_from_is_public': False,
                'last_modified_by': None,
                'last_modified_from': None,
                'last_modified_from_is_public': False,
            })

            # For debugging purposes.
            self.stdout.write(
                self.style.SUCCESS(_('Promoted member slug %(slug)s to area coordinator.')%{
                    'slug': member.user.slug,
                })
            )

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
