# -*- coding: utf-8 -*-
"""
Example:
python manage.py setup_resource_server_authorization "bart@mikasoftware.com"
"""
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
from oauthlib.common import generate_token
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    AbstractAccessToken,
    AccessToken,
    RefreshToken
)

from shared_foundation.models import SharedUser


class Command(BaseCommand):
    help = _('Adds a oAuth 2.0 application to the server.')

    def handle(self, *args, **options):
        application, created = Application.objects.update_or_create(
            name=settings.NWAPP_RESOURCE_SERVER_NAME,
            defaults={
                "user": None,
                "name": settings.NWAPP_RESOURCE_SERVER_NAME,
                "skip_authorization": True,
                "authorization_grant_type": AbstractApplication.GRANT_PASSWORD,
                "client_type": AbstractApplication.CLIENT_CONFIDENTIAL
            }
        )
        self.stdout.write(
            self.style.SUCCESS(_('Resource Server - Auth Type: %(type)s') % {
                'type': str(AbstractApplication.GRANT_PASSWORD)
            })
        )

        # # Create our our access token.
        # aware_dt = timezone.now()
        # expires_dt = aware_dt.replace(aware_dt.year + 1776)
        # access_token, created = AccessToken.objects.update_or_create(
        #     application=application,
        #     defaults={
        #         'user': None,
        #         'application': application,
        #         'expires': expires_dt,
        #         'token': generate_token(),
        #         'scope': 'read,write,introspection'
        #     },
        #     scope='read,write,introspection'
        # )
        #
        # # STEP 3: Return our ID values.
        # self.stdout.write(
        #     self.style.SUCCESS(_('Resource Server - Auth Type: %(type)s') % {
        #         'type': str(AbstractApplication.GRANT_PASSWORD)
        #     })
        # )
        # self.stdout.write(
        #     self.style.SUCCESS(_('Resource Server - Client ID: %(client_id)s') % {
        #         'client_id': application.client_id
        #     })
        # )
        # self.stdout.write(
        #     self.style.SUCCESS(_('Resource Server - Client Secret: %(client_secret)s') % {
        #         'client_secret': application.client_secret
        #     })
        # )
        # self.stdout.write(
        #     self.style.SUCCESS(_('Resource Server - Access Token: %(access_token)s') % {
        #         'access_token': str(access_token)
        #     })
        # )
