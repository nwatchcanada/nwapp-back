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
# from tenant_api.serializers.watch_comment import WatchCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Watch,
    PrivateImageUpload,
    Tag
)


class WatchAvatarCreateOrUpdateOperationSerializer(serializers.ModelSerializer):
    watch = serializers.SlugField(required=True, write_only=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(write_only=True, allow_null=False,)
    upload_filename = serializers.CharField(write_only=True, allow_null=False,)

    # Meta Information.
    class Meta:
        model = PrivateImageUpload
        fields = (
            'watch',

            # REACT-DJANGO UPLOAD | STEP 2 OF 4: Define required fields.
            'upload_content',
            'upload_filename',
        )

    def validate_watch(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not Watch.objects.filter(user__slug=value).exists():
            raise serializers.ValidationError("Watch does not exist")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Extract the data we are processing.
        slug = validated_data.get('watch')
        watch = Watch.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')

        # Extract our upload file data
        content = validated_data.get('upload_content')
        filename = validated_data.get('upload_filename')
        if settings.DEBUG:
            filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

        # Create our private image upload if it was not done previously,
        # else we update the watch's avatar.
        if watch.avatar_image == None or watch.avatar_image is None:
            watch.avatar_image = PrivateImageUpload.objects.create(
                image_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentFile`, Django handles all file uploading.
                user = watch.user,
                created_by = request.user,
                created_from = request.client_ip,
                created_from_is_public = request.client_ip_is_routable,
                last_modified_by = request.user,
                last_modified_from = request.client_ip,
                last_modified_from_is_public = request.client_ip_is_routable,
            )
            watch.last_modified_by = request.user
            watch.last_modified_from = request.client_ip
            watch.last_modified_from_is_public = request.client_ip_is_routable
            watch.save()
            print("WatchAvatarCreateOrUpdateOperationSerializer --> create() --> CREATED IMAGE")
        else:
            watch.avatar_image.image_file = content_file
            watch.avatar_image.last_modified_by = request.user
            watch.avatar_image.last_modified_from = request.client_ip
            watch.avatar_image.last_modified_from_is_public = request.client_ip_is_routable
            watch.avatar_image.save()
            watch.last_modified_by = request.user
            watch.last_modified_from = request.client_ip
            watch.last_modified_from_is_public = request.client_ip_is_routable
            watch.save()
            print("WatchAvatarCreateOrUpdateOperationSerializer --> create() --> UPDATED IMAGE")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return validated_data
