# -*- coding: utf-8 -*-
import logging
import django_rq
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
from drf_extra_fields.geo_fields import PointField

from shared_foundation.models import SharedOrganization
from shared_organization.tasks import create_organization_func


logger = logging.getLogger(__name__)


class SharedOrganizationListCreateSerializer(serializers.ModelSerializer):

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
    police_report_url = serializers.CharField(
        required=False,
        allow_blank=True,
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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Create our `Tenant` object.
        #-----------------------------
        django_rq.enqueue(create_organization_func, validated_data)

        # Return our output
        return validated_data
