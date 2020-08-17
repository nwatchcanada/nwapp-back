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
    District, Associate, AreaCoordinator, Member
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


def report_05_streaming_csv_view(request):
    today = timezone.now()
    districts = District.objects.all().order_by("id")

    # Convert our aware datetimes to the specific timezone of the tenant.
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Business Watches Report","","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"", "",],)
    rows += (["", "", "", "", "",],)
    rows += (["", "", "", "",],)

    # Generate the CSV header row.
    rows += ([
        "Name",
        "Associate Count",
        "Watch Coun",
        "Member Count",
        "Tags"
    ],)

    # Generate the CSV dataset.
    for district in districts.all():

        a_count = Associate.objects.filter(
            Q(watch__district=district)|
            Q(user__area_coordinator__watch__district=district)|
            Q(user__member__watch__district=district)
        ).count()
        ac_count = AreaCoordinator.objects.filter(watch__district=district).count()
        m_count = Member.objects.filter(watch__district=district).count()

        # Generate our row.
        rows += ([
            district.name,
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
    response['Content-Disposition'] = 'attachment; filename="business_watches.csv"'
    return response
