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
from shared_foundation.models import SharedUser
# from tenant_foundation.constants import *
from tenant_foundation.models import Watch, Tag, StreetAddressRange
from tenant_foundation.serializers import TagListCreateSerializer
from tenant_watch.serializers.street_membership_serializers import StreetAddressRangeRetrieveSerializer


logger = logging.getLogger(__name__)


class WatchRetrieveSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    type_of = serializers.IntegerField()
    type_of_label = serializers.CharField(source="get_type_of_label")
    name = serializers.CharField()
    description = serializers.CharField()
    district_type_of = serializers.IntegerField(source="district.type_of",read_only=True,)
    district_type_of_code = serializers.CharField(source="district.get_type_of_code",read_only=True,)
    district_slug = serializers.SlugField(source="district.slug",read_only=True,)
    district_name = serializers.CharField(source="district.name",read_only=True,)
    tags = TagListCreateSerializer(many=True,)
    is_archived = serializers.BooleanField()
    # street_membership = StreetAddressRangeRetrieveSerializer(many=True, source="street_address_ranges",)
    street_membership = serializers.SerializerMethodField()

    def get_street_membership(self, watch_obj):
        """
        Override the `street_membership` field to include filtering for
        non-archived records.
        """
        try:
            active_street_address_ranges = watch_obj.street_address_ranges.filter(is_archived=False)
            s = StreetAddressRangeRetrieveSerializer(
                active_street_address_ranges,
                many=True,
            )
            return s.data
        except Exception as e:
            print(e)
            return []
