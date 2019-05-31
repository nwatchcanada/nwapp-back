# -*- coding: utf-8 -*-
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from djmoney.money import Money
from oauthlib.common import generate_token

from shared_foundation.constants import *
from shared_foundation.models import SharedOrganization, SharedGroup


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py init_app
    """

    help = _('Sets up the web-application for the first time.')

    def handle(self, *args, **options):
        '''
        Create the default store of our application.
        '''
        organization = SharedOrganization.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'schema': 'public',
                'name': 'Public Domain',
                'description': 'Used as shared domain.',
                'country': "Canada",
                "region": "Ontario",
                "locality": "London",
            }
        )
        SharedGroup.objects.update_or_create(id=1, defaults={'id': 1, 'name': 'Executive'})
        SharedGroup.objects.update_or_create(id=2, defaults={'id': 2, 'name': 'Manager'})
        SharedGroup.objects.update_or_create(id=3, defaults={'id': 3, 'name': 'Frontline Staff'})
        SharedGroup.objects.update_or_create(id=4, defaults={'id': 4, 'name': 'Associate'})
        SharedGroup.objects.update_or_create(id=5, defaults={'id': 5, 'name': 'Area Coordinator'})
        SharedGroup.objects.update_or_create(id=6, defaults={'id': 6, 'name': 'Member'})

        # from django.contrib.sites.models import Site # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#caching-the-current-site-object
        # current_site = Site.objects.get_current()
        # current_site.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN
        # current_site.save()
        #
        # self.stdout.write(
        #     self.style.SUCCESS(_('Successfully updated site object.'))
        # )
