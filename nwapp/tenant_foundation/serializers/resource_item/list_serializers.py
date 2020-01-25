# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from tenant_foundation.models import ResourceItem


logger = logging.getLogger(__name__)


class ResourceItemListSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    category = serializers.IntegerField(read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    name = serializers.CharField(
        read_only=True,
        allow_blank=False,
        allow_null=False,
    )
    uuid = serializers.UUIDField(
        read_only=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    last_modified_at = serializers.DateTimeField(read_only=True, allow_null=False,)
