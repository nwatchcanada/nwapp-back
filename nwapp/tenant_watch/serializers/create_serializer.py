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


class StreetAddressRangeCreateSerializer(serializers.Serializer):
    street_number_start = serializers.IntegerField()
    street_number_finish = serializers.IntegerField()
    street_name = serializers.CharField()
    street_type = serializers.IntegerField()
    street_type_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    street_direction = serializers.IntegerField()

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        watch = self.context.get('watch')
        street_number_start = validated_data.get('street_number_start')
        street_number_finish = validated_data.get('street_number_finish')
        street_name = validated_data.get('street_name')
        street_type = validated_data.get('street_type')
        street_type_other = validated_data.get('street_type_other')
        street_direction = validated_data.get('street_direction')
        obj = StreetAddressRange.objects.create(
            watch = watch,
            street_number_start = street_number_start,
            street_number_end = street_number_finish,
            street_name = street_name,
            street_type = street_type,
            street_type_other = street_type_other,
            street_direction = street_direction,
            is_archived = False,
            created_by=request.user,
            created_from=request.client_ip,
            created_from_is_public=request.client_ip_is_routable,
            last_modified_by=request.user,
            last_modified_from=request.client_ip,
            last_modified_from_is_public=request.client_ip_is_routable,
        )
        return obj


class WatchCreateSerializer(serializers.Serializer):
    type_of = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_null=True,
        required=False,
    )
    name = serializers.CharField()
    description = serializers.CharField()
    district = serializers.SlugField()
    street_membership = serializers.JSONField()

    def validate_district(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not District.objects.filter(slug=value).exists():
            raise serializers.ValidationError("District does not exist")
        return value

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        type_of = validated_data.get('type_of')
        name = validated_data.get('name')
        description = validated_data.get('description')
        district_slug = validated_data.get('district')
        tags = validated_data.get('tags')
        street_membership = validated_data.get('street_membership')

        district = District.objects.get(slug=district_slug)

        watch = Watch.objects.create(
            type_of = type_of,
            name = name,
            description = description,
            district = district,
            is_archived = False,
            created_by=request.user,
            created_from=request.client_ip,
            created_from_is_public=request.client_ip_is_routable,
            last_modified_by=request.user,
            last_modified_from=request.client_ip,
            last_modified_from_is_public=request.client_ip_is_routable,
        )

        # Attached our tags.
        if tags is not None:
            if len(tags) > 0:
                watch.tags.set(tags)
                logger.info("Attached tag to watch.")

        # Iterate through all the street addresses and process.
        for data in street_membership:
            s = StreetAddressRangeCreateSerializer(
                data=data,
                context={
                    'request': request,
                    'watch': watch,
                }
            );
            s.is_valid(raise_exception=True)
            s.save()

        logger.info("Created watch contact.")

    #     '''
    #     Run in the background the code which will `process` the newly created
    #     watch object.
    #     '''
    #     django_rq.enqueue(
    #         process_watch_with_slug_func,
    #         request.tenant.schema_name,
    #         watch.user.slug
    #     )
    #
        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return watch
