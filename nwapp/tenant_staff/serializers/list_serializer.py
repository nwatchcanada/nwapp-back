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
from tenant_foundation.models import Staff


logger = logging.getLogger(__name__)


class StaffListSerializer(serializers.Serializer):
    type_of = serializers.IntegerField(source="user.member.type_of", read_only=True,)
    organization_name = serializers.CharField(
        allow_blank=False,
        validators=[],
        source="user.member.contact.organization_name",
        read_only=True,
    )
    organization_type_of = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        source="user.member.contact.organization_type_of",
    )
    first_name = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.contact.first_name",
    )
    last_name = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.contact.last_name",
    )
    primary_phone_e164 = E164PhoneNumberField(allow_null=False, read_only=True,source="user.member.contact.primary_phone",)
    primary_phone_national = NationalPhoneNumberField(allow_null=False, read_only=True,source="user.member.contact.primary_phone",)
    email = serializers.EmailField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.contact.email",
    )
    slug = serializers.SlugField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.slug",
    )
    street_address = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.address.street_address",
    )
    country = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.address.country",
    )
    region = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.address.region",
    )
    locality = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.address.locality",
    )
    postal_code = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[],
        source="user.member.address.postal_code",
    )
    state = serializers.CharField(
        read_only=True,
        source="user.member.state",
    )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'user',
            'user__groups',
            'user__member__contact',
            'user__member__address',
            'user__member__metric',
            'created_by',
            'last_modified_by'
        )
        return queryset
