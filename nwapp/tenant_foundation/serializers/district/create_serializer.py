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

from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string # REACT-DJANGO UPLOAD | STEP 2 OF 4
from tenant_foundation.models import District, PrivateImageUpload

logger = logging.getLogger(__name__)


class DistrictCreateSerializer(serializers.Serializer):
    type_of = serializers.ChoiceField(
        required=True,
        allow_null=False,
        choices=District.TYPE_OF_CHOICES,
        write_only=True,
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=District.objects.all(),
            )
        ],
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    counselor_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    counselor_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    counselor_phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    website_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )

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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        type_of = validated_data.get('type_of')
        description = validated_data.get('description')
        name = validated_data.get('name')
        counselor_name = validated_data.get('counselor_name')
        counselor_email = validated_data.get('counselor_email')
        counselor_phone = validated_data.get('counselor_phone')
        website_url = validated_data.get('website_url')

        try:
            # Extract our upload file data
            content = validated_data.get('upload_content')
            filename = validated_data.get('upload_filename')
            if settings.DEBUG:
                filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
            content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

            # Create our file.
            private_file = PrivateImageUpload.objects.create(
                title = "District Business Logo",
                description = "-",
                is_archived = False,
                # user = user,
                data_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentImage`, Django handles all file uploading.
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )
            print("Private file created") #TODO: Remove `print` when ready.
        except Exception as e:
            private_file = None

        # Create the district.
        district = District.objects.create(
            type_of=type_of,
            description=description,
            name=name,
            counselor_name=counselor_name,
            counselor_email=counselor_email,
            counselor_phone=counselor_phone,
            website_url=website_url,
            logo_image=private_file,
        )

        logger.info("New district was been created.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return district
