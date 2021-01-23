# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.constants import MEMBER_GROUP_ID
from shared_foundation.drf.fields import E164PhoneNumberField, NationalPhoneNumberField
from shared_foundation.utils import get_content_file_from_base64_string
from shared_foundation.models import SharedUser
from tenant_foundation.models import District


logger = logging.getLogger(__name__)


class DistrictUpdateSerializer(serializers.Serializer):
    slug = serializers.SlugField(write_only=True,)
    type_of = serializers.IntegerField(write_only=True, required=True,)
    name = serializers.CharField(write_only=True, required=True,)
    description = serializers.CharField(write_only=True, required=False,)
    counselor_name = serializers.CharField(write_only=True, required=False,)
    counselor_email = serializers.EmailField(write_only=True, required=False,)
    counselor_phone = serializers.CharField(write_only=True, required=False,)
    website_url = serializers.URLField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(write_only=True, required=False,)
    facebook_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=False,
    )
    upload_filename = serializers.CharField(
        write_only=True,
        allow_null=True,
        allow_blank=True,
        required=False,
    )

    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.type_of = validated_data.get('type_of')
        instance.description = validated_data.get('description')
        instance.name = validated_data.get('name')
        instance.counselor_name = validated_data.get('counselor_name', None)
        instance.counselor_email = validated_data.get('counselor_email', None)
        instance.counselor_phone = validated_data.get('counselor_phone', None)
        instance.website_url = validated_data.get('website_url', None)
        instance.facebook_url = validated_data.get('facebook_url', None)
        instance.created_by = request.user
        instance.created_from = request.client_ip
        instance.created_from_is_public = request.client_ip_is_routable
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable
        instance.save()
        logger.info("New district was been updated.")

        try:
            # Extract our upload file data
            content = validated_data.get('upload_content', None)
            filename = validated_data.get('upload_filename', None)

            if content and filename:
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
                logger.info("Private file was been created.")
                instance.logo_image = private_file
                instance.save()
        except Exception as e:
            print(e)
            private_file = None

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
