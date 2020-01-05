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
from tenant_foundation.models import (
    Associate
)


class Command(BaseCommand):
    help = _('TODO: GIVE DESCRIPTION.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py process_associate_with_slug "london" "bartlomiej-mika-fauG"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('slug', nargs='+', type=str)

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

        associate = Associate.objects.filter(user__slug=slug).first()
        if associate:
            self.process(associate)

            # For debugging purposes.
            self.stdout.write(
                self.style.SUCCESS(_('Successfully processed associate with slug %(slug)s.') %{
                    'slug': slug,
                })
            )
        else:
            raise CommandError(_('Associate does not exist with slug %(slug)s.')%{
                'slug': slug
            })

    @transaction.atomic
    def process(self, associate):
        freezer = freeze_time(associate.last_modified_at)
        freezer.start()
        self.process_searchable_content(associate)
        freezer.stop()

    def process_searchable_content(self, associate):
        text = ""
        text += associate.contact.get_searchable_content()
        text += " " + associate.address.get_searchable_content()
        text += " " + associate.metric.get_searchable_content()
        associate.indexed_text = text
        associate.save()
