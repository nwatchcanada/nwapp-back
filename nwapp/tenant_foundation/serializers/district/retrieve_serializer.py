# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.constants import MEMBER_GROUP_ID
from shared_foundation.drf.fields import E164PhoneNumberField, NationalPhoneNumberField
from shared_foundation.utils import get_arr_from_point, get_multi_arr_from_polygon
from shared_foundation.models import SharedUser
from tenant_foundation.models import District


logger = logging.getLogger(__name__)


class DistrictRetrieveSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    type_of_label = serializers.CharField(source="get_type_of_label",read_only=True,)
    type_of_code = serializers.CharField(source="get_type_of_code",read_only=True,)
    name = serializers.CharField(read_only=True,)
    description = serializers.CharField(read_only=True,)
    counselor_name = serializers.CharField(read_only=True,)
    counselor_email = serializers.EmailField(read_only=True,)
    counselor_phone = serializers.CharField(read_only=True,)
    website_url = serializers.URLField(read_only=True,)
    is_archived = serializers.BooleanField(read_only=True,)
    logo_image = serializers.ImageField(
        source="logo_image.image_file",
        allow_null=True,
    )
    boundry_zoom = serializers.IntegerField(read_only=True,)
    boundry_position = serializers.SerializerMethodField()
    boundry_polygon = serializers.SerializerMethodField()

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)
    last_modified__at = serializers.DateTimeField(read_only=True, allow_null=False,)

    def get_boundry_position(self, obj):
        return get_arr_from_point(obj.boundry_position)

    def get_boundry_polygon(self, obj):
        return get_multi_arr_from_polygon(obj.boundry_polygon)
