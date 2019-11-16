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
from shared_foundation.models import SharedOrganization


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

    class Meta:
        model = SharedOrganization
        fields = (
            # Thing
            'id',
            'created_at',
            'last_modified_at',
            'alternate_name',
            'description',
            'name',
            # 'url',
            'timezone_name',

            # Postal Address
            'country',
            'locality',
            'region',

            # Tenancy
            'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset


class SharedOrganizationUpdateSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = SharedOrganization
        fields = (
            # Thing
            'id',
            'created_at',
            'last_modified_at',
            'alternate_name',
            'description',
            'name',
            # 'url',
            'timezone_name',

            # Postal Address
            'country',
            'locality',
            'region',

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
        instance.url = validated_data.get('url', instance.url)
        instance.timezone_name = validated_data.get('timezone_name', instance.timezone_name)

        instance.country = validated_data.get('country', instance.country)
        instance.locality = validated_data.get('locality', instance.locality)
        instance.region = validated_data.get('region', instance.region)
        
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.save()

        # Return our output
        return validated_data
