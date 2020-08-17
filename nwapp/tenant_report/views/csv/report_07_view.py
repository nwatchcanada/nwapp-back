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
    Watch, Associate, AreaCoordinator, Member
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


def report_07_streaming_csv_view(request):
    today = timezone.now()
    watches = Watch.objects.filter(type_of=Watch.TYPE_OF.RESIDENTIAL).order_by("id")

    # Convert our aware datetimes to the specific timezone of the tenant.
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Residential Report","","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"", "",],)
    rows += (["", "", "", "", "",],)
    rows += (["", "", "", "",],)

    # Generate the CSV header row.
    rows += ([
        "Name",
        "Associate Count",
        "Area Coordinator Count",
        "Member Count",
        "Tags"
    ],)

    # Generate the CSV dataset.
    for watch in watches.all():

        a_count = Associate.objects.filter(
            Q(watch=watch)|
            Q(user__area_coordinator__watch=watch)|
            Q(user__member__watch=watch)
        ).count()
        ac_count = AreaCoordinator.objects.filter(watch=watch).count()
        m_count = Member.objects.filter(watch=watch).count()

        # Generate our row.
        rows += ([
            watch.name,
            a_count,
            ac_count,
            m_count,
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="residential.csv"'
    return response
