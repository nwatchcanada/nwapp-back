# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template.loader import render_to_string    # HTML to TXT
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from shared_foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    """
    Example:
    python manage.py send_reset_password_email bart@mikasoftware.com
    """
    help = 'Command will send password reset link to the user account.'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+')

    def handle(self, *args, **options):
        try:
            for email in options['email']:
                me = SharedUser.objects.get(email__iexact=email)
                self.begin_processing(me)

        except SharedUser.DoesNotExist:
            raise CommandError(_('Account does not exist with the email or username: %s') % str(email))

    def begin_processing(self, me):
        pr_access_code = me.generate_pr_code()

        # Generate the links.
        url = settings.NWAPP_FRONTEND_HTTP_PROTOCOL+settings.NWAPP_FRONTEND_HTTP_DOMAIN+"/reset-password/"+str(pr_access_code)
        web_view_url = reverse_with_full_domain(
            reverse_url_id='nwapp_reset_password_email',
            resolve_url_args=[pr_access_code]
        )
        subject = "NWApp: Password Reset"
        param = {
            'url': url,
            'web_view_url': web_view_url,
            'me': me
        }

        # For debugging purposes only.
        print("---------------------------------------------------------------")
        print("URL", url)
        print("WEB URL", web_view_url)
        print("---------------------------------------------------------------")

        # DEVELOPERS NOTE:
        # https://templates.mailchimp.com/resources/inline-css/

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('account/email/reset_password_email_view.txt', param)
        html_content = render_to_string('account/email/reset_password_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [me.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        self.stdout.write(
            self.style.SUCCESS(_('NWApp: Sent welcome email to %s.') % str(me.email))
        )
