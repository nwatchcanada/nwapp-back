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
from tenant_foundation.models import Item, ItemType, PrivateImageUpload, PrivateFileUpload


logger = logging.getLogger(__name__)


class ResourceDetailsUpdateSerializer(serializers.Serializer):

    title = serializers.CharField(
        required=True,
        allow_null=False,
    )
    description = serializers.CharField(
        required=True,
        allow_null=False,
    )
    external_url = serializers.URLField(
        required=False,
        allow_null=True,
    )
    embed_code = serializers.CharField(
        required=False,
        allow_null=True,
    )
    resource_image = serializers.JSONField(
       required=False,
       allow_null=True,
    )
    resource_file = serializers.JSONField(
       required=False,
       allow_null=True,
    )

    def create_resource_image(self, request, validated_data):
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

    def create_resource_file(self, request, validated_data):
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

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        title = validated_data.get('title')
        description = validated_data.get('description')
        external_url = validated_data.get('external_url')
        embed_code = validated_data.get('embed_code')
        resource_image = validated_data.get('resource_image')
        resource_file = validated_data.get('resource_file')

        # Attach the file upload.
        if instance.format_type == Item.FORMAT_TYPE.IMAGE_RESOURCE_TYPE_OF:
            # DEVELOPERS NOTE:
            # (1) The following code will either update the `resource_image` or
            #     create a new image.
            # (2) Check to see if a previous image was uploaded and if so then
            #     we need to delete it.
            resource_image_slug = resource_image.get("slug", None)
            if resource_image_slug:
                instance.resource_image__slug = resource_image_slug
            else:
                if instance.resource_image:
                    instance.resource_image.delete()
                instance.resource_image = self.create_resource_image(request, validated_data)

        elif instance.format_type == Item.FORMAT_TYPE.FILE_RESOURCE_TYPE_OF:
            # DEVELOPERS NOTE:
            # (1) The following code will either update the `resource_file` or
            #     create a new image.
            # (2) Check to see if a previous file was uploaded and if so then
            #     we need to delete it.
            resource_file_slug = resource_file.get("slug", None)
            if resource_file_slug:
                instance.resource_file__slug = resource_file_slug
            else:
                if instance.resource_file:
                    instance.resource_file.delete()
                instance.resource_file = self.create_resource_file(request, validated_data)

        # Save it.
        instance.title = title
        instance.description = description
        instance.external_url = external_url
        instance.embed_code = embed_code
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
