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
from tenant_foundation.models import Associate, AssociateAddress


class Command(BaseCommand):
    help = _('Command will attempt to lookup the longitude and latitude of the staff\'s address from a third-party geocoding API web-service.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py geocode_staff_address "london" "ryan-adams"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('staff_slug', nargs='+', type=str)

    @transaction.atomic
    def process(self, area_coordinator_address):
        # Add secure SSL context to every request.
        # (https://github.com/geopy/geopy/issues/124)
        import certifi
        import ssl
        import geopy.geocoders
        ctx = ssl.create_default_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx

        # from geopy.geocoders import GoogleV3
        # geolocator = GoogleV3(api_key=settings.GOOGLE_MAP_API_KEY)

        # Note: https://geopy.readthedocs.io/en/stable/#
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="nwApp")

        # geolocator = Nominatim()
        area_coordinator_address_str = area_coordinator_address.postal_address_without_postal_code
        location = geolocator.geocode(area_coordinator_address_str, exactly_one=True)
        if location:
            area_coordinator_address.position = Point(location.latitude,location.longitude)
            area_coordinator_address.needs_geocoding = False
            area_coordinator_address.geocoding_succeeded_at = timezone.now()
            # print(location.raw) # For debugging purposes only.
            self.stdout.write(
                self.style.SUCCESS(_('Succeeded geocoding staff %(slug)s with latitude and longitude of %(lt)s, %(ln)s')%{
                    'slug': area_coordinator_address.member.user.slug,
                    'ln':location.longitude,
                    'lt':location.latitude,
                })
            )
        else:
            area_coordinator_address.geocoding_failed_at = timezone.now()
            self.stdout.write(
                self.style.WARNING(_('Failed geocoding staff %(slug)s')%{
                    'slug': area_coordinator_address.member.user.slug,
                })
            )
        area_coordinator_address.save()

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Get the user inputs.
        schema_name = options['schema_name'][0]
        staff_slug = options['staff_slug'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Lookup our staff.
        area_coordinator_address = AssociateAddress.objects.filter(
            member__user__slug=staff_slug
        ).first()
        if area_coordinator_address is None:
            raise CommandError(_('Staff\'s address does not exist!'))

        if area_coordinator_address.needs_geocoding is False:
            raise CommandError(_('Staff\'s geo-location was already found.'))

        # Process.
        freezer = freeze_time(area_coordinator_address.last_modified_at)
        freezer.start()
        self.process(area_coordinator_address)
        freezer.stop()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully finished geocoding'))
        )
