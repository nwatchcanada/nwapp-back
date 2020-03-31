# -*- coding: utf-8 -*-
from freezegun import freeze_time
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from django.db import connection # Used for django tenants.
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from django.utils import timezone

from shared_foundation.models import SharedOrganization
from tenant_foundation.models import Member
from shared_foundation.utils import get_point_from_ip


class Command(BaseCommand):
    help = _('Command will attempt to lookup the longitude and latitude from the IP address.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py geoip2_member_audit "london" "diana-adkins"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('member_slug', nargs='+', type=str)

    @transaction.atomic
    def process(self, member):
        if member.created_from:
            member.created_from_position = get_point_from_ip(member.created_from)
        if member.last_modified_from:
            member.last_modified_from_position = get_point_from_ip(member.last_modified_from)
        member.save()

        if member.address.created_from:
            member.address.created_from_position = get_point_from_ip(member.address.created_from)
        if member.address.last_modified_from:
            member.address.last_modified_from_position = get_point_from_ip(member.address.last_modified_from)
        member.address.save()

        if member.contact.created_from:
            member.contact.created_from_position = get_point_from_ip(member.contact.created_from)
        if member.contact.last_modified_from:
            member.contact.last_modified_from_position = get_point_from_ip(member.contact.last_modified_from)
        member.contact.save()

        if member.metric.created_from:
            member.metric.created_from_position = get_point_from_ip(member.metric.created_from)
        if member.metric.last_modified_from:
            member.metric.last_modified_from_position = get_point_from_ip(member.metric.last_modified_from)
        member.metric.save()

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Get the user inputs.
        schema_name = options['schema_name'][0]
        member_slug = options['member_slug'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Lookup our member.
        member = Member.objects.filter(user__slug=member_slug).first()
        if member is None:
            raise CommandError(_('Member does not exist!'))

        # Process.
        freezer = freeze_time(member.last_modified_at)
        freezer.start()
        self.process(member)
        freezer.stop()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully finished geocoding'))
        )
