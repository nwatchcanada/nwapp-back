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

from shared_foundation.utils import get_content_file_from_base64_string # REACT-DJANGO UPLOAD | STEP 2 OF 4
from tenant_foundation.models import ResourceItem, PrivateImageUpload, PrivateFileUpload


logger = logging.getLogger(__name__)


class ResourceItemCreateSerializer(serializers.Serializer):
    category = serializers.IntegerField(write_only=True,)
    type_of = serializers.IntegerField(write_only=True,)
    name = serializers.CharField(
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=ResourceItem.objects.all(),
            )
        ],
    )
    external_url = serializers.URLField(write_only=True, allow_null=True, allow_blank=True,)
    embed_code = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,)
    description = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(
        write_only=True,
        allow_null=False,
        required=False,
    )
    upload_filename = serializers.CharField(
        write_only=True,
        allow_null=False,
        required=False,
    )

    def create_image(self, request, validated_data):
        try:
            # Extract our upload file data
            content = validated_data.get('upload_content')
            filename = validated_data.get('upload_filename')
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
            content = validated_data.get('upload_content')
            filename = validated_data.get('upload_filename')
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

            # Create our file.
            private_file = PrivateFileUpload.objects.create(
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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        category = validated_data.get('category')
        type_of = validated_data.get('type_of')
        name = validated_data.get('name')
        external_url = validated_data.get('external_url')
        embed_code = validated_data.get('embed_code')
        description = validated_data.get('description')
        # text = validated_data.get('text')

        # Create the district.
        resource_item = ResourceItem.objects.create(
            category = category,
            type_of = type_of,
            name = name,
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

        logger.info("New tag was been created.")

        # Attach the file upload.
        if type_of == ResourceItem.TYPE_OF.IMAGE_RESOURCE_TYPE_OF:
            resource_item.image = self.create_image(request, validated_data)
            resource_item.save()
        elif type_of == ResourceItem.TYPE_OF.FILE_RESOURCE_TYPE_OF:
            resource_item.file = self.create_file(request, validated_data)
            resource_item.save()

        # print(private_file)
        # print("\n")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return resource_item
