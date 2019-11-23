# -*- coding: utf-8 -*-
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# from djmoney.money import Money
# from oauthlib.common import generate_token

from shared_foundation.constants import *
from shared_foundation.models import SharedOrganization, SharedOrganizationDomain, SharedGroup


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py init_app
    """

    help = _('Sets up the web-application for the first time.')

    def process_site(self):
        """
        Site
        """
         # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#caching-the-current-site-object
        current_site = Site.objects.get_current()
        current_site.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN
        current_site.name = "NWApp"
        current_site.save()
        self.stdout.write(
            self.style.SUCCESS(_('Update site domain and name.'))
        )

    def process_group(self):
        SharedGroup.objects.update_or_create(id=EXECUTIVE_GROUP_ID, defaults={'id': EXECUTIVE_GROUP_ID, 'name': 'Executive'})
        SharedGroup.objects.update_or_create(id=MANAGEMENT_GROUP_ID, defaults={'id': MANAGEMENT_GROUP_ID, 'name': 'Manager'})
        SharedGroup.objects.update_or_create(id=FRONTLINE_GROUP_ID, defaults={'id': FRONTLINE_GROUP_ID, 'name': 'Frontline Staff'})
        SharedGroup.objects.update_or_create(id=ASSOCIATE_GROUP_ID, defaults={'id': ASSOCIATE_GROUP_ID, 'name': 'Associate'})
        SharedGroup.objects.update_or_create(id=AREA_COORDINATOR_GROUP_ID, defaults={'id': AREA_COORDINATOR_GROUP_ID, 'name': 'Area Coordinator'})
        SharedGroup.objects.update_or_create(id=MEMBER_GROUP_ID, defaults={'id': MEMBER_GROUP_ID, 'name': 'Member'})
        self.stdout.write(
            self.style.SUCCESS(_('Updated shared groups.'))
        )

    def process_public_tenant(self):
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
            self.stdout.write(
                self.style.WARNING(_('Minor issue when saving `SharedOrganizationDomain`, the error is:\n%(e)s.') % {
                    'e': str(e)
                })
            )

        self.stdout.write(
            self.style.SUCCESS(_('Updated or created public tenant.'))
        )

    def handle(self, *args, **options):
        '''
        Create the default store of our application.
        '''
        self.process_public_tenant()
        self.process_site()
        self.process_group()
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated site object.'))
        )
