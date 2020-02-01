# -*- coding: utf-8 -*-
import logging
import django_rq
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.drf.fields import E164PhoneNumberField
from shared_foundation.models import SharedUser, SharedGroup
# from tenant_foundation.constants import *
from tenant_foundation.models import Watch, Tag, District, StreetAddressRange
from tenant_watch.tasks import process_watch_with_slug_func


logger = logging.getLogger(__name__)


class StreetAddressRangeRetrieveSerializer(serializers.Serializer):
    street_address = serializers.CharField(source="__str__", read_only=True,)
    slug = serializers.SlugField()
    street_number_start = serializers.IntegerField()
    street_number_end = serializers.IntegerField()
    street_name = serializers.CharField()
    street_type = serializers.IntegerField()
    street_type_other = serializers.CharField()
    street_type_label = serializers.CharField(source="get_street_type_label",)
    street_direction = serializers.IntegerField()
    street_direction_label = serializers.CharField(source="get_street_direction_label",)
    is_archived = serializers.BooleanField()


class StreetAddressRangeCreateSerializer(serializers.Serializer):
    street_address = serializers.CharField(source="__str__", read_only=True,)
    street_number_start = serializers.IntegerField()
    street_number_end = serializers.IntegerField()
    street_name = serializers.CharField()
    street_type = serializers.IntegerField()
    street_type_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    street_direction = serializers.IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
    )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        watch = self.context.get('watch')
        street_number_start = validated_data.get('street_number_start')
        street_number_end = validated_data.get('street_number_end')
        street_name = validated_data.get('street_name')
        street_type = validated_data.get('street_type')
        street_type_other = validated_data.get('street_type_other', "")
        street_direction = validated_data.get('street_direction', 0)
        is_archived = validated_data.get('is_archived', False)
        obj = StreetAddressRange.objects.create(
            watch = watch,
            street_number_start = street_number_start,
            street_number_end = street_number_end,
            street_name = street_name,
            street_type = street_type,
            street_type_other = street_type_other,
            street_direction = street_direction,
            is_archived = is_archived,
            created_by=request.user,
            created_from=request.client_ip,
            created_from_is_public=request.client_ip_is_routable,
            last_modified_by=request.user,
            last_modified_from=request.client_ip,
            last_modified_from_is_public=request.client_ip_is_routable,
        )
        return obj


class StreetAddressRangeUpdateSerializer(serializers.Serializer):
    street_address = serializers.CharField(source="__str__", read_only=True,)
    street_number_start = serializers.IntegerField(write_only=True,)
    street_number_end = serializers.IntegerField(write_only=True,)
    street_name = serializers.CharField(write_only=True,)
    street_type = serializers.IntegerField(write_only=True,)
    street_type_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    street_direction = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
    )

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        request = self.context.get('request')
        watch = self.context.get('watch')
        instance.street_number_start = validated_data.get('street_number_start')
        instance.street_number_end = validated_data.get('street_number_end')
        instance.street_name = validated_data.get('street_name')
        instance.street_type = validated_data.get('street_type')
        instance.street_type_other = validated_data.get('street_type_other', "")
        instance.street_direction = validated_data.get('street_direction', 0)
        instance.is_archived = validated_data.get('is_archived', False,)
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()
        return instance
