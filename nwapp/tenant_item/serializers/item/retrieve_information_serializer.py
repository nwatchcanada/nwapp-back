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

from tenant_foundation.models import Item, ItemType


logger = logging.getLogger(__name__)


class InformationItemRetrieveSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    type_of_text = serializers.CharField(read_only=True,source="type_of.text",)
    type_of_slug = serializers.CharField(read_only=True,source="type_of.slug",)
    # category = serializers.SlugField(
    #     required=True,
    #     allow_null=False,
    # )
    description = serializers.CharField(
        required=False,
        allow_null=True,
    )
