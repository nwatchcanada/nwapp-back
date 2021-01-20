# -*- coding: utf-8 -*-
import django_rq
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # HTML to TXT

from foundation import constants
from foundation.models import User
from foundation.utils import reverse_with_full_domain
from foundation.model_resources import get_staff_email_addresses


class Command(BaseCommand):
    """
    Example:
    python manage.py send_user_was_created_to_staff_email 1
    """
    help = _('Command will send an activation email to the user based on the email.')

    def add_arguments(self, parser):
        # User Account.
        parser.add_argument('email' , nargs='+', type=str)

    def handle(self, *args, **options):
        email = options['email'][0]

        try:
            for email in options['email']:
                user = User.objects.get(email=email)
                self.begin_processing(user)
        except User.DoesNotExist:
            raise CommandError(_('Account does not exist with the email: %s') % str(email))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('NWAPP: Activation email was sent successfully.'))
        )

    def begin_processing(self, user):
        # Generate the data.
        url = settings.NWAPP_BACKEND_HTTP_PROTOCOL+settings.NWAPP_BACKEND_HTTP_DOMAIN+"/en/admin/foundation/user/"+str(user.id)+"/change/"
        web_view_url = reverse_with_full_domain(
            reverse_url_id='nwapp_user_was_created_email',
            resolve_url_args=[user.id]
        )
        subject = "New user to NWApp!"
        param = {
            'user': user,
            'url': url,
            'web_view_url': web_view_url,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('account/email/user_was_created_email.txt', param)
        html_content = render_to_string('account/email/user_was_created_email.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = get_staff_email_addresses()

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
