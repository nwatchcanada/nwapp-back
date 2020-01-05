# -*- coding: utf-8 -*-
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
# from tenant_api.serializers.associate_comment import MemberCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    PrivateFileUpload,
    Tag,
    Comment,
    MemberComment,
    AreaCoordinatorComment,
)


class PrivateFileUploadCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugField(required=True, write_only=True,)
    title = serializers.CharField(required=True, allow_null=False, write_only=True,)
    description = serializers.CharField(required=True, allow_null=False, write_only=True,)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True, write_only=True,)
    is_archived = serializers.BooleanField(required=True, write_only=True,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(
        write_only=True,
        allow_null=False,
        required=True,
    )
    upload_filename = serializers.CharField(
        write_only=True,
        allow_null=False,
        required=True,
    )

    def validate_user(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not SharedUser.objects.filter(slug=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    # Meta Information.
    class Meta:
        model = PrivateFileUpload
        fields = (
            'user',
            'title',
            'description',
            'tags',
            'is_archived',

            # REACT-DJANGO UPLOAD | STEP 2 OF 4: Define required fields.
            'upload_content',
            'upload_filename',
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('user')
        user = SharedUser.objects.get(slug=slug)
        request = self.context.get("request")

        #-----------------------------
        # Create our file.
        #-----------------------------

        # Extract our upload file data
        content = validated_data.get('upload_content')
        filename = validated_data.get('upload_filename')
        if settings.DEBUG:
            filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

        # Create our file.
        private_file = PrivateFileUpload.objects.create(
            title = validated_data.get('title'),
            description = validated_data.get('description'),
            is_archived = validated_data.get('is_archived'),
            user = user,
            data_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentFile`, Django handles all file uploading.
            created_by = request.user,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable,
            last_modified_by = request.user,
            last_modified_from = request.client_ip,
            last_modified_from_is_public = request.client_ip_is_routable,
        )

        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                private_file.tags.set(tags)

        # For debugging purposes only.
        print("Created private file #", private_file)

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        text = _("A file named \"%(filename)s\" has been uploaded to this member's record by %(name)s.") % {
            'filename': str(filename),
            'name': str(request.user),
        }
        comment = Comment.objects.create(
            created_by = request.user,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable,
            last_modified_by = request.user,
            last_modified_from = request.client_ip,
            last_modified_from_is_public = request.client_ip_is_routable,
            text=text
        )

        if user.is_member:
            MemberComment.objects.create(
                member=user.member,
                comment=comment,
            )
            print("Created comment for member")
        elif user.is_area_coordinator:
            AreaCoordinatorComment.objects.create(
                area_coordinator=user.area_coordinator,
                comment=comment,
            )
            print("Created comment for area coordinator")
        else:
            raise serializers.ValidationError({
                "error": "Programmer did not write the code for this yet.",
            })

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        # Return our validated data.
        return private_file
