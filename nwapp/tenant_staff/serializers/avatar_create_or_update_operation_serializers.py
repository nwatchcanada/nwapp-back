# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
# from tenant_api.serializers.staff_comment import StaffCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Staff,
    PrivateImageUpload,
    Tag
)


class StaffAvatarCreateOrUpdateOperationSerializer(serializers.ModelSerializer):
    staff = serializers.SlugField(required=True, write_only=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(write_only=True, allow_null=False,)
    upload_filename = serializers.CharField(write_only=True, allow_null=False,)

    # Meta Information.
    class Meta:
        model = PrivateImageUpload
        fields = (
            'staff',

            # REACT-DJANGO UPLOAD | STEP 2 OF 4: Define required fields.
            'upload_content',
            'upload_filename',
        )

    def validate_staff(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not Staff.objects.filter(user__slug=value).exists():
            raise serializers.ValidationError("Staff does not exist")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Extract the data we are processing.
        slug = validated_data.get('staff')
        staff = Staff.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')

        # Extract our upload file data
        content = validated_data.get('upload_content')
        filename = validated_data.get('upload_filename')
        if settings.DEBUG:
            filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

        # Create our private image upload if it was not done previously,
        # else we update the staff's avatar.
        if staff.avatar_image == None or staff.avatar_image is None:
            staff.avatar_image = PrivateImageUpload.objects.create(
                image_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentFile`, Django handles all file uploading.
                user = staff.user,
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )
            staff.last_modified_by = request.user
            staff.last_modified_from = request.client_ip
            staff.last_modified_from_is_public = request.client_ip_is_routable
            staff.save()
            print("StaffAvatarCreateOrUpdateOperationSerializer --> create() --> CREATED IMAGE")
        else:
            staff.avatar_image.image_file = content_file
            staff.avatar_image.last_modified_by = request.user
            staff.avatar_image.last_modified_from = request.client_ip
            staff.avatar_image.last_modified_from_is_public = request.client_ip_is_routable
            staff.avatar_image.save()
            staff.last_modified_by = request.user
            staff.last_modified_from = request.client_ip
            staff.last_modified_from_is_public = request.client_ip_is_routable
            staff.save()
            print("StaffAvatarCreateOrUpdateOperationSerializer --> create() --> UPDATED IMAGE")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return validated_data
