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

from tenant_foundation.models import ResourceItem


logger = logging.getLogger(__name__)


class ResourceItemRetrieveUpdateDestroySerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    category = serializers.IntegerField()
    category_label = serializers.CharField(read_only=True, source="get_category_label",)
    type_of = serializers.IntegerField()
    type_of_label = serializers.CharField(read_only=True, source="get_type_of_label",)
    name = serializers.CharField()
    description = serializers.CharField()
    external_url = serializers.URLField()
    embed_code = serializers.CharField()
    image_url = serializers.ImageField(
        read_only=True,
        max_length=None,
        use_url=True,
        source="image.image_file",
        allow_null=True,
    )
    is_archived = serializers.BooleanField()

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_at = serializers.DateTimeField(read_only=True, allow_null=False,)
