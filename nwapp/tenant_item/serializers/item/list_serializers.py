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

from tenant_foundation.models import ItemType


logger = logging.getLogger(__name__)


class ItemListSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    category = serializers.IntegerField(
        read_only=True,
        source="type_of.category"
    )
    category_label = serializers.CharField(
        read_only=True,
        source='type_of.get_category_label',
    )
    created_at = serializers.DateTimeField(read_only=True,)
    state = serializers.CharField(read_only=True,)
    text = serializers.CharField(read_only=True, source="__str__")
    is_archived = serializers.CharField(read_only=True,)

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'type_of',
            # 'created_by', 'last_modified_by'
        )
        return queryset
