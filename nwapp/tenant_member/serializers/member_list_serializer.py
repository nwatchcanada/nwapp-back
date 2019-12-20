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
# from tenant_foundation.constants import *
from tenant_foundation.models import Member


logger = logging.getLogger(__name__)


class MemberListSerializer(serializers.Serializer):
    type_of = serializers.IntegerField()
    organization_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
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
    primary_phone_e164 = E164PhoneNumberField(allow_null=False, required=True,source="contact.primary_phone",)
    primary_phone_national = NationalPhoneNumberField(allow_null=False, required=True,source="contact.primary_phone",)
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        validators=[],
        source="contact.email",
    )
    slug = serializers.SlugField(
        required=True,
        allow_blank=False,
        validators=[],
        source="user.slug",
    )
    street_address = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address.street_address",
    )
    country = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address.country",
    )
    region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address.region",
    )
    locality = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address.locality",
    )
    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address.postal_code",
    )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'user', 'contact', 'address', 'metric', 'created_by', 'last_modified_by'
        )
        return queryset
