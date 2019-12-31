# -*- coding: utf-8 -*-
import phonenumbers
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

from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
# from tenant_api.serializers.member_comment import MemberCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Member,
    PrivateImageUpload,
    Tag
)


class MemberAvatarCreateOrUpdateOperationSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(many=False, queryset=Member.objects.all(), required=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(write_only=True, allow_null=False,)
    upload_filename = serializers.CharField(write_only=True, allow_null=False,)

    # Meta Information.
    class Meta:
        model = PrivateImageUpload
        fields = (
            'id',
            'member',

            # REACT-DJANGO UPLOAD | STEP 2 OF 4: Define required fields.
            'upload_content',
            'upload_filename',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'member',
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Extract the member we are processing.
        member = validated_data.get('member')

        # Extract our upload file data
        content = validated_data.get('upload_content')
        filename = validated_data.get('upload_filename')
        if settings.DEBUG:
            filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

        # Create our private image upload if it was not done previously,
        # else we update the member's avatar.
        if member.avatar_image == None or member.avatar_image is None:
            member.avatar_image = PrivateImageUpload.objects.create(
                image_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentFile`, Django handles all file uploading.
                created_by = self.context['created_by'],
                created_from = self.context['created_from'],
                created_from_is_public = self.context['created_from_is_public'],
                last_modified_by = self.context['created_by'],
                last_modified_from = self.context['created_from'],
                last_modified_from_is_public = self.context['created_from_is_public'],
            )
            member.last_modified_by = self.context['created_by']
            member.last_modified_from = self.context['created_from']
            member.last_modified_from_is_public = self.context['created_from_is_public']
            member.save()
        else:
            member.avatar_image.image_file = content_file
            member.avatar_image.last_modified_by = self.context['created_by']
            member.avatar_image.last_modified_from = self.context['created_from']
            member.avatar_image.last_modified_from_is_public = self.context['created_from_is_public']
            member.avatar_image.save()
            member.last_modified_by = self.context['created_by']
            member.last_modified_from = self.context['created_from']
            member.last_modified_from_is_public = self.context['created_from_is_public']
            member.save()

        return validated_data
