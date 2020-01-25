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
from tenant_foundation.models import ResourceItem, PrivateImageUpload


logger = logging.getLogger(__name__)


class ResourceItemRetrieveUpdateDestroySerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    category = serializers.IntegerField()
    category_label = serializers.CharField(read_only=True, source="get_category_label",)
    type_of = serializers.IntegerField()
    type_of_label = serializers.CharField(read_only=True, source="get_type_of_label",)
    name = serializers.CharField()
    description = serializers.CharField()
    external_url = serializers.URLField(required=False, allow_null=True, allow_blank=True,)
    embed_code = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    image_url = serializers.ImageField(
        read_only=True,
        max_length=None,
        use_url=True,
        source="image.image_file",
        allow_null=True,
    )
    is_archived = serializers.BooleanField()

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

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_at = serializers.DateTimeField(read_only=True, allow_null=False,)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.type_of = validated_data.get('type_of')
        instance.category = validated_data.get('category')
        instance.description = validated_data.get('description')
        instance.name = validated_data.get('name')
        instance.external_url = validated_data.get('external_url')
        instance.created_by = request.user
        instance.created_from = request.client_ip
        instance.created_from_is_public = request.client_ip_is_routable
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable
        instance.save()
        logger.info("New district was been updated.")

        # try:
        #     # Extract our upload file data
        #     content = validated_data.get('upload_content', None)
        #     filename = validated_data.get('upload_filename', None)
        #
        #     if content and filename:
        #         if settings.DEBUG:
        #             filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        #         content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.
        #
        #         # Create our file.
        #         private_file = PrivateImageUpload.objects.create(
        #             is_archived = False,
        #             user = request.user,
        #             image_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentImage`, Django handles all file uploading.
        #             created_by = request.user,
        #             created_from = request.client_ip,
        #             created_from_is_public = request.client_ip_is_routable,
        #             last_modified_by = request.user,
        #             last_modified_from = request.client_ip,
        #             last_modified_from_is_public = request.client_ip_is_routable,
        #         )
        #         logger.info("Private file was been created.")
        #         instance.logo_image = private_file
        #         instance.save()
        # except Exception as e:
        #     print(e)
        #     private_file = None

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
