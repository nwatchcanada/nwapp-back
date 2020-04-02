# -*- coding: utf-8 -*-
import logging
import django_rq
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from drf_extra_fields.geo_fields import PointField

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_arr_from_point


logger = logging.getLogger(__name__)


class SharedOrganizationRetrieveSerializer(serializers.ModelSerializer):

    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    schema_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=SharedOrganization.objects.all())],
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    alternate_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    timezone_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    street_type = serializers.IntegerField(
        read_only=True,
    )

    street_type_label = serializers.CharField(
        read_only=True,
        source="get_pretty_street_type",
    )

    street_direction_label = serializers.CharField(
        read_only=True,
        source="get_pretty_street_direction",
    )

    police_report_url = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    default_position = serializers.SerializerMethodField()
    default_zoom = serializers.IntegerField(required=False,)

    class Meta:
        model = SharedOrganization
        fields = (
            'id',
            'created_at',
            'last_modified_at',
            'alternate_name',
            'description',
            'name',
            # 'url',
            'timezone_name',
            'police_report_url',

            # Postal Address
            'country',
            'city',
            'province',
            'street_number',
            'street_name',
            'apartment_unit',
            'street_type',
            'street_type_other',
            'street_type_label',
            'street_direction',
            'street_direction_label',
            'postal_code',
            'default_position',
            'default_zoom',

            # Tenancy
            'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset

    def get_default_position(self, obj):
        return get_arr_from_point(obj.default_position)


class SharedOrganizationUpdateSerializer(serializers.ModelSerializer):

    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    alternate_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    timezone_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    police_report_url = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    street_type = serializers.IntegerField(
        required=True,
    )
    default_position = PointField(required=False)
    default_zoom = serializers.IntegerField(required=False,)

    class Meta:
        model = SharedOrganization
        fields = (
            'id',
            'created_at',
            'last_modified_at',
            'alternate_name',
            'description',
            'name',
            # 'url',
            'timezone_name',
            'police_report_url',

            # Postal Address
            'country',
            'city',
            'province',
            'street_number',
            'street_name',
            'apartment_unit',
            'street_type',
            'street_type_other',
            'street_direction',
            'postal_code',
            'default_position',
            'default_zoom',

            # Tenancy
            'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        instance.alternate_name = validated_data.get('alternate_name', instance.alternate_name)
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        # instance.url = validated_data.get('url', instance.url)
        instance.timezone_name = validated_data.get('timezone_name', instance.timezone_name)
        instance.police_report_url = validated_data.get('police_report_url', instance.police_report_url)

        instance.country = validated_data.get('country', instance.country)
        instance.city = validated_data.get('city', instance.city)
        instance.province = validated_data.get('province', instance.province)
        instance.street_number = validated_data.get('street_number', instance.street_number)
        instance.street_name = validated_data.get('street_name', instance.street_name)
        instance.apartment_unit = validated_data.get('apartment_unit', instance.apartment_unit)
        instance.street_type = validated_data.get('street_type', instance.street_type)
        instance.street_type_other = validated_data.get('street_type_other', instance.street_type_other)
        instance.street_direction = validated_data.get('street_direction', instance.street_direction)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.default_position = validated_data.get('default_position', instance.default_position)
        instance.default_zoom = validated_data.get('default_zoom', instance.default_zoom)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.save()

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        # Return our output
        return validated_data
