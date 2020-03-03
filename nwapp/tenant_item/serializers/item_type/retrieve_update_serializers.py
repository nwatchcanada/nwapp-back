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


class ItemTypeRetrieveUpdateDestroySerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    category = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    category_label = serializers.CharField(
        read_only=True,
        source='get_category_label',
    )
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[
            UniqueValidator(
                queryset=ItemType.objects.all(),
            )
        ],
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    state = serializers.CharField(read_only=True)
    state_label = serializers.CharField(read_only=True, source="get_state_label()")

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_at = serializers.DateTimeField(read_only=True, allow_null=False,)

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        instance.category = validated_data.get('category')
        instance.text = validated_data.get('text')
        instance.description = validated_data.get('description')
        instance.created_by = request.user
        instance.created_from = request.client_ip
        instance.created_from_is_public = request.client_ip_is_routable
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Updated item.")

        return instance
