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


class Command(BaseCommand):
    help = _('Command will attempt to lookup the longitude and latitude of the member\'s address from a third-party geocoding API web-service.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py geocode_member_address "london" "diana-adkins"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('member_slug', nargs='+', type=str)

    @transaction.atomic
    def process(self, member):
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
        member_address_str = member.address.postal_address_without_postal_code
        location = geolocator.geocode(member_address_str, exactly_one=True)
        if location:
            member.address.position = Point(location.latitude,location.longitude)
            member.address.needs_geocoding = False
            member.address.geocoding_succeeded_at = timezone.now()
            # print(location.raw) # For debugging purposes only.
            self.stdout.write(
                self.style.SUCCESS(_('Succeeded geocoding member %(slug)s with latitude and longitude of %(lt)s, %(ln)s')%{
                    'slug': member.user.slug,
                    'ln':location.longitude,
                    'lt':location.latitude,
                })
            )
        else:
            member.address.geocoding_failed_at = timezone.now()
            self.stdout.write(
                self.style.WARNING(_('Failed geocoding member %(slug)s')%{
                    'slug': member.user.slug,
                })
            )
        member.address.save()

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        member_slug = options['member_slug'][0]

        if SharedOrganization.activate_tenant_by_schema(schema_name) == False:
            raise CommandError(_('Organization does not exist!'))

        # Lookup our member.
        member = Member.objects.filter(user__slug=member_slug).first()
        if member is None:
            raise CommandError(_('Member does not exist!'))

        if member.address.needs_geocoding is False:
            raise CommandError(_('Member\'s geo-location was already found.'))

        # Process.
        freezer = freeze_time(member.last_modified_at)
        freezer.start()
        self.process(member)
        freezer.stop()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully finished geocoding'))
        )
