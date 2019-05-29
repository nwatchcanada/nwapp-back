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
from shared_foundation.models import SharedOrganization


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
                'subdomain': 'public',
                'name': 'Public Domain',
                'description': 'Used as shared domain.'
            }
        )
