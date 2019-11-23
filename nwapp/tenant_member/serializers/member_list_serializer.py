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
from shared_foundation.drf.fields import PhoneNumberField


logger = logging.getLogger(__name__)


class MemberListSerializer(serializers.Serializer):
    type_of = serializers.IntegerField()
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
    primary_phone = PhoneNumberField(allow_null=False, required=True,source="contact.primary_phone",)
    e164_primary_phone = serializers.SerializerMethodField()
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

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'user', 'contact', 'address', 'metric', 'created_by', 'last_modified_by'
        )
        return queryset

    def get_e164_primary_phone(self, obj):
        """
        Converts the "PhoneNumber" object into a "E164" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.contact.primary_phone:
                return phonenumbers.format_number(obj.contact.primary_phone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            print("get_e164_primary_phone", e)
            return None
