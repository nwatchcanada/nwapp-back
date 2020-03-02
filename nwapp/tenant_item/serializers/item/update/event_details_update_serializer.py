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

from shared_foundation.utils import get_content_file_from_base64_string
from tenant_foundation.models import Item, ItemType, PrivateImageUpload


logger = logging.getLogger(__name__)


class EventDetailsUpdateSerializer(serializers.Serializer):

    title = serializers.CharField(
        required=True,
        allow_null=False,
    )
    description = serializers.CharField(
        required=True,
        allow_null=False,
    )
    event_logo_image = serializers.JSONField(
       required=False,
       allow_null=True,
    )
    external_url = serializers.URLField(
        required=False,
        allow_null=True,
    )
    shown_to_whom = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    can_be_posted_on_social_media = serializers.BooleanField(
        required=False,
        allow_null=True,
    )

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        title = validated_data.get("title")
        description = validated_data.get('description')
        event_logo_image = validated_data.get('event_logo_image')
        external_url = validated_data.get('external_url')
        shown_to_whom = validated_data.get('shown_to_whom')
        can_be_posted_on_social_media = validated_data.get('can_be_posted_on_social_media')

        # Save it.
        instance.title = title
        instance.description = description
        # # instance.event_logo_image = event_logo_image
        instance.external_url = external_url
        instance.shown_to_whom = shown_to_whom
        instance.can_be_posted_on_social_media = can_be_posted_on_social_media
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
