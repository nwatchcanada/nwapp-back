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
from shared_foundation.utils import get_arr_from_point, get_multi_arr_from_polygon
from tenant_foundation.models import Watch, District


logger = logging.getLogger(__name__)


class WatchListSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=Watch.STATE_CHOICES,read_only=True,)
    type_of = serializers.ChoiceField(choices=Watch.TYPE_OF_CHOICES, read_only=True,)
    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    district_type_of = serializers.ChoiceField(
        choices=Watch.TYPE_OF_CHOICES,
        read_only=True,
        source="district.type_of"
    )
    district_type_of_code = serializers.CharField(
        source="district.get_type_of_code",
        read_only=True,
    )
    district_name = serializers.CharField(
        required=True,
        allow_blank=False,
        source="district.name"
    )
    district_slug = serializers.CharField(
        required=True,
        allow_blank=False,
        source="district.slug"
    )
    slug = serializers.SlugField(
        required=True,
        allow_blank=False,
    )
    is_virtual = serializers.BooleanField(
        required=True,
    )
    boundry_position = serializers.SerializerMethodField()
    boundry_polygon = serializers.SerializerMethodField()

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'district',
            'created_by',
            'last_modified_by'
        )
        return queryset

    def get_boundry_position(self, obj):
        return get_arr_from_point(obj.boundry_position)

    def get_boundry_polygon(self, obj):
        return get_multi_arr_from_polygon(obj.boundry_polygon)
