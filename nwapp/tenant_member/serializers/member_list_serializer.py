# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


# from tenant_foundation.constants import *
from tenant_foundation.models import Member


logger = logging.getLogger(__name__)


class MemberListSerializer(serializers.Serializer):
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        source="contact.organization_name",
    )
    organization_type_of = serializers.IntegerField(
        required=False,
        allow_null=True,
        source="contact.organization_type_of",
    )
    first_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="contact.first_name",
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="contact.last_name",
    )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'contact', 'address', 'metric', 'created_by', 'last_modified_by'
        )
        return queryset
