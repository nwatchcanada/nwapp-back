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

from shared_foundation.utils import get_content_file_from_base64_string
from tenant_foundation.models import Item, ItemType, PrivateImageUpload, PrivateFileUpload


logger = logging.getLogger(__name__)


class ResourceItemCreateSerializer(serializers.Serializer):
    category = serializers.SlugField(write_only=True,)
    type_of = serializers.IntegerField(write_only=True,)
    name = serializers.CharField(write_only=True,)
    format_type = serializers.IntegerField(write_only=True,)
    external_url = serializers.URLField(write_only=True, allow_null=True, allow_blank=True, required=False,)
    embed_code = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, required=False,)
    description = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    resource_image = serializers.JSONField(
       required=False,
       allow_null=True,
    )
    resource_file = serializers.JSONField(
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

    def create_image(self, request, validated_data):
        try:
            # Extract our upload file data
            resource_image = validated_data.get('resource_image', None)
            content = resource_image.get('data', None)
            filename = resource_image.get('file_name', None)
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

            # Create our file.
            private_file = PrivateImageUpload.objects.create(
                is_archived = False,
                user = request.user,
                image_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentImage`, Django handles all file uploading.
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )
            logger.info("Private image was been created.")
            return private_file
        except Exception as e:
            print(e)
            private_file = None
            return None

    def create_file(self, request, validated_data):
        try:
            # Extract our upload file data
            resource_file = validated_data.get('resource_file', None)
            content = resource_file.get('data', None)
            filename = resource_file.get('file_name', None)
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

            # Create our file.
            private_file = PrivateFileUpload.objects.create(
                is_archived = False,
                user = request.user,
                data_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentImage`, Django handles all file uploading.
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )
            logger.info("Private file was been created.")
            return private_file
        except Exception as e:
            print(e)
            private_file = None
            return None

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        category = validated_data.get('category')
        # type_of = validated_data.get('type_of')
        format_type = validated_data.get('format_type')
        name = validated_data.get('name')
        external_url = validated_data.get('external_url')
        embed_code = validated_data.get('embed_code', None)
        description = validated_data.get('description', None)
        # text = validated_data.get('text')
        resource_file = validated_data.get('resource_file', None)
        resource_image = validated_data.get('resource_image', None)

        item_type = ItemType.objects.filter(slug=category).first()

        # Create the district.
        resource_item = Item.objects.create(
            # category = category,
            type_of = item_type,
            format_type = format_type,
            title = name,
            external_url = external_url,
            embed_code = embed_code,
            description = description,
            created_by = request.user,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable,
            last_modified_by = request.user,
            last_modified_from = request.client_ip,
            last_modified_from_is_public = request.client_ip_is_routable,
        )

        # Attach the file upload.
        if format_type == Item.FORMAT_TYPE.IMAGE_RESOURCE_TYPE_OF:
            resource_item.resource_image = self.create_image(request, validated_data)
            resource_item.save()
        elif format_type == Item.FORMAT_TYPE.FILE_RESOURCE_TYPE_OF:
            resource_item.resource_file = self.create_file(request, validated_data)
            resource_item.save()

        # print(private_file)
        # print("\n")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return resource_item
