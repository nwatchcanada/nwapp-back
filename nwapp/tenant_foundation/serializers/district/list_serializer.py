# -*- coding: utf-8 -*-
import logging
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

from shared_foundation.drf.fields import E164PhoneNumberField, NationalPhoneNumberField
from tenant_foundation.models import District


logger = logging.getLogger(__name__)


class DistrictListSerializer(serializers.Serializer):
    type_of = serializers.ChoiceField(
        allow_null=False,
        choices=District.TYPE_OF_CHOICES,
        read_only=True,
    )
    name = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    description = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    counselor_name = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    counselor_email = serializers.EmailField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    counselor_phone = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    website_url = serializers.URLField(
        allow_blank=True,
        allow_null=True,
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        allow_null=True,
        read_only=True,
    )
    last_modified_at = serializers.DateTimeField(
        allow_null=True,
        read_only=True,
    )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'created_by', 'last_modified_by',
        )
        return queryset
