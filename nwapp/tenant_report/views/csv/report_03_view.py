# -*- coding: utf-8 -*-
import datetime
from dateutil import parser
from djmoney.money import Money
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Extract
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from shared_foundation.constants import *
from shared_foundation.utils import *
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Member
)

"""
Code below was taken from:
https://docs.djangoproject.com/en/2.0/howto/outputting-csv/
"""

import csv
from django.http import StreamingHttpResponse

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def report_03_streaming_csv_view(request):
    today = timezone.now()
    members = Member.objects.filter(
        Q(user__is_active=True)
    ).select_related("user", "watch", "watch__district",)

    # Convert our aware datetimes to the specific timezone of the tenant.
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Members Report","","","","", ""],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"", "", "", ""],)
    rows += (["", "", "", "", "", ""],)
    rows += (["", "", "", "", "", ""],)

    # Generate the CSV header row.
    rows += ([
        "Member No.",
        # "Role",
        "Member Name",
        "Ward",
        "E-Mail",
        "Primary Phone",
        "Watch Name",
        "Join Date",
        "Tags"
    ],)

    # Generate the CSV dataset.
    for member in members.all():
    #
    #     # Preformat our `wsib_number` variable.
    #     wsib_number = "-" if associate.wsib_number is None else associate.wsib_number
    #     wsib_number = "-" if len(wsib_number) == 0 else wsib_number
    #
    #     # Generate our row.
        rows += ([
            member.user_id,
            str(member),
            str(member.watch.district.name),
            member.user.email,
            str(member.user.member.contact.primary_phone),
            str(member.user.member.watch),
            pretty_dt_string(member.user.created_at),
    #         "-" if associate.commercial_insurance_expiry_date is None else pretty_dt_string(associate.commercial_insurance_expiry_date),
    #         "-" if associate.auto_insurance_expiry_date is None else pretty_dt_string(associate.auto_insurance_expiry_date),
    #         wsib_number,
    #         "-" if associate.wsib_insurance_date is None else pretty_dt_string(associate.wsib_insurance_date),
    #         associate.get_insurance_requirements()
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    return response
