# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


logger = logging.getLogger(__name__)


class SharedProfileInfoRetrieveUpdateSerializer(serializers.Serializer):
    # --- Authentication Credentials ---
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    schema_name = serializers.CharField(read_only=True, source="tenant.schema_name",)
    role_id = serializers.SerializerMethodField()

    # --- User Details ---
    slug = serializers.SlugField(read_only=True,)
    email = serializers.CharField(required=True,allow_blank=False,)
    first_name = serializers.CharField(required=True,allow_blank=False,)
    middle_name = serializers.CharField(required=False,allow_blank=True,)
    last_name = serializers.CharField(required=True,allow_blank=False,)
    # avatar = serializers.CharField(required=False,allow_blank=True,)
    # birthdate = serializers.CharField(required=False,allow_blank=True,)
    # nationality = serializers.CharField(required=False,allow_blank=True,)
    # gender = serializers.CharField(required=False,allow_blank=True,)

    # --- Tenant Details ---
    tenant_country = serializers.CharField(read_only=True, source="tenant.country",)
    tenant_region = serializers.CharField(read_only=True, source="tenant.region",)
    tenant_locality = serializers.CharField(read_only=True, source="tenant.locality",)
    tenant_timezone = serializers.CharField(read_only=True, source="tenant.timezone_name",)

    def get_role_id(self, obj):
        group = obj.groups.first()
        group_id = None
        if group:
            group_id = group.id
        return group_id

    def get_access_token(self, obj):
        access_token = self.context.get('access_token', None)
        if access_token:
            return {
                'token': str(access_token),
                'expires': int(access_token.expires.timestamp()),
                'scope': str(access_token.scope)
            }
        return None

    def get_refresh_token(self, obj):
        refresh_token = self.context.get('refresh_token', None)
        if refresh_token:
            revoked_at = int(refresh_token.revoked.timestamp()) if refresh_token.revoked is not None else None
            return {
                'token': str(refresh_token),
                'revoked': revoked_at,
            }
        return None
