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

        # DEVELOPERS NOTE:
        # (1) The following code will either update the `event_logo_image` or
        #     create a new image.
        # (2) Check to see if a previous image was uploaded and if so then
        #     we need to delete it.
        event_logo_image_slug = event_logo_image.get("slug")
        if event_logo_image_slug:
            instance.event_logo_image__slug = event_logo_image_slug
        else:
            # print(event_logo_image) # For debugging purposes only.
            data = event_logo_image.get('data', None)
            filename = event_logo_image.get('file_name', None)
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(data, filename)

            if instance.event_logo_image:
                instance.event_logo_image.delete()
                instance.event_logo_image = None

            private_image = PrivateImageUpload.objects.create(
                item = instance,
                user = request.user,
                image_file = content_file,
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )

            instance.event_logo_image = private_image
            # print("Created - event_logo_image")

        # Save it.
        instance.title = title
        instance.description = description
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
