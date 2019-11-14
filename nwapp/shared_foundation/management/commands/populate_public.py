# -*- coding: utf-8 -*-
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.models import SharedOrganization
from shared_foundation.models import SharedOrganizationDomain


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py populate_public
    """

    help = _('Loads all the data necessary to operate this application.')

    def handle(self, *args, **options):
        #create your public tenant

        public_tenant, created = SharedOrganization.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'schema_name': 'public',
                'name': 'Public Domain',
                'description': 'Used as shared domain.',
                'country': "Canada",
                "region": "Ontario",
                "locality": "London",
            }
        )

        # Add one or more domains for the tenant
        domain = SharedOrganizationDomain()
        domain.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN # don't add your port or www here! on a local server you'll want to use localhost here
        domain.tenant = public_tenant
        domain.is_primary = True
        try:
            domain.save()
        except Exception as e:
            logger.exception(e)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup public database.'))
        )

        # First call; current site fetched from database.
        from django.contrib.sites.models import Site # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#caching-the-current-site-object
        current_site = Site.objects.get_current()
        current_site.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN
        current_site.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated public.'))
        )
