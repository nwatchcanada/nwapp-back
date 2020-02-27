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


class EventItemCreateSerializer(serializers.Serializer):
    # --- COMMON --- #
    type_of = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    category = serializers.SlugField(
        required=True,
        allow_null=False,
    )

    # --- EVENT --- #
    start_date_time = serializers.DateTimeField(
        required=False,
        allow_null=False,
    )
    is_all_day_event = serializers.BooleanField(
        required=False,
        allow_null=False,
    )
    finish_date_time = serializers.DateTimeField(
        required=False,
        allow_null=False,
    )
    title = serializers.CharField(
        required=False,
        allow_null=True,
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
    )
    event_logo_image = serializers.JSONField(
       required=False,
       allow_null=True,
    )
    photos = serializers.JSONField(
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

    def validate_category(self, value):
        """
        Add extra validation.
        (1) Lookup `ItemType` based on `category`.
        (2) Lookup `ItemType` based on `slug`.
        """
        type_of = self.context.get("type_of")
        does_exist = ItemType.objects.filter(
            slug=value,
            category=type_of
        ).exists()
        if does_exist:
            return value
        else:
            raise serializers.ValidationError(_("Item type does not exist."))

    def validate_start_date_time(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing start date / time."))

    def validate_finish_date_time(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing finish date / time."))

    def validate_title(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing title."))

    def validate_description(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing description."))

    def validate_shown_to_whom(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing description."))

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        type_of = self.context.get("type_of")
        category = validated_data.get('category')
        is_all_day_event = validated_data.get('is_all_day_event')
        start_date_time = validated_data.get('start_date_time')
        finish_date_time = validated_data.get('finish_date_time')
        title = validated_data.get('title')
        description = validated_data.get('description')
        external_url = validated_data.get('external_url')
        shown_to_whom = validated_data.get('shown_to_whom')
        can_be_posted_on_social_media = validated_data.get('can_be_posted_on_social_media')
        event_logo_image = validated_data.get('event_logo_image', None)
        photos = validated_data.get('photos', [])

        item_type = ItemType.objects.filter(slug=category).first()

        item = Item.objects.create(
            type_of=item_type,
            start_at=start_date_time,
            is_all_day_event=is_all_day_event,
            finish_at=finish_date_time,
            title=title,
            description=description,
            external_url=external_url,
            shown_to_whom=shown_to_whom,
            can_be_posted_on_social_media=can_be_posted_on_social_media,
            created_by=request.user,
            created_from=request.client_ip,
            created_from_is_public=request.client_ip_is_routable,
            last_modified_by=request.user,
            last_modified_from=request.client_ip,
            last_modified_from_is_public=request.client_ip_is_routable,
        )

        # Proccess the uploaded photos which are encoded in `base64` format.
        # The following code will convert the `base64` string into a Python
        # binary data and save it in our database.
        if photos != None and photos != "" and len(photos) > 0:
            for photo in photos:
                data = photo['data']
                filename = photo['file_name']
                if settings.DEBUG:
                    filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
                content_file = get_content_file_from_base64_string(data, filename)

                private_image = PrivateImageUpload.objects.create(
                    item = item,
                    user = request.user,
                    image_file = content_file,
                    created_by = request.user,
                    created_from = request.client_ip,
                    created_from_is_public = request.client_ip_is_routable,
                    last_modified_by = request.user,
                    last_modified_from = request.client_ip,
                    last_modified_from_is_public = request.client_ip_is_routable,
                )

        if event_logo_image:
            # print(event_logo_image) # For debugging purposes only.
            data = event_logo_image.get('data', None)
            filename = event_logo_image.get('file_name', None)
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(data, filename)

            private_image = PrivateImageUpload.objects.create(
                item = item,
                user = request.user,
                image_file = content_file,
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )

            item.event_logo_image = private_image
            item.save()
            # print("Created - event_logo_image")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return item
