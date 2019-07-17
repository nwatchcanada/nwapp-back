# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.models import SharedOrganization, SharedUser, SharedGroup


class Command(BaseCommand):
    help = _('Command will create an admin account.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_regular_user "london" "bart+regular@mikasoftware.com" "123password" "Bart" "Mika" 6;
        """
        parser.add_argument('tenant_schema', nargs='+', type=str)
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('first_name', nargs='+', type=str)
        parser.add_argument('last_name', nargs='+', type=str)
        parser.add_argument('group_membership', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        # Get the user inputs.
        tenant_schema = options['tenant_schema'][0]
        email = options['email'][0]
        password = options['password'][0]
        first_name = options['first_name'][0]
        last_name = options['last_name'][0]
        group_membership_id = options['group_membership'][0]

        tenant = SharedOrganization.objects.filter(schema=tenant_schema).first()
        if tenant is None:
            raise CommandError(_('Organization could not be found.'))

        # Defensive Code: Prevent continuing if the email already exists.
        if SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email already exists, please pick another email.'))

        group_membership = SharedGroup.objects.filter(id=group_membership_id).first()
        if group_membership is None:
            raise CommandError(_('Group could not be found.'))

        # Create the user.
        user = SharedUser.objects.create(
            tenant=tenant,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            was_email_activated=True,
            billing_given_name = first_name,
            billing_last_name = last_name,
            billing_email = email,
            shipping_given_name = first_name,
            shipping_last_name = last_name,
            shipping_email = email
        )

        user.groups.add(group_membership)

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully created a regular account.'))
        )
