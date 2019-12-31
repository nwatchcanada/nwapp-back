# -*- coding: utf-8 -*-
import logging
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
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Member,
    MemberComment,
)


logger = logging.getLogger(__name__)


class MemberArchiveOperationSerializer(serializers.Serializer):
    member = serializers.PrimaryKeyRelatedField(many=False, queryset=Member.objects.all(), required=True)
    state = serializers.CharField(required=True, allow_blank=False)
    deactivation_reason = serializers.CharField(required=True, allow_blank=False)
    deactivation_reason_other = serializers.CharField(required=True, allow_blank=True)
    comment = serializers.CharField(required=True, allow_blank=False)

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------------#
        # Get validated POST & context data #
        #-----------------------------------#
        member = validated_data.get('member')
        state = validated_data.get('state')
        deactivation_reason = validated_data.get('deactivation_reason', None)
        deactivation_reason_other = validated_data.get('deactivation_reason_other', None)
        comment_text = validated_data.get('comment')
        user = self.context['user']
        from_ip = self.context['from']
        from_is_public = self.context['from_is_public']

        raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
            "error": "Terminating for debugging purposes only."
        })

        #------------------------------------------#
        # Create any comments explaining decision. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            text = comment_text,
            created_by = user,
            created_from = from_ip,
            created_from_is_public = from_is_public,
            last_modified_by = user,
            last_modified_from = from_ip,
            last_modified_from_is_public = from_is_public,
        )
        MemberComment.objects.create(
            about=member,
            comment=comment_obj,
        )
        # For debugging purposes only.
        logger.info("Member comment created.")

        #-------------------------#
        # Update member object. #
        #-------------------------#
        member.state = state
        member.deactivation_reason = deactivation_reason
        member.deactivation_reason_other = deactivation_reason_other
        member.last_modified_by = user
        member.last_modified_from = from_ip
        member.last_modified_from_is_public = from_is_public
        member.save()

        # For debugging purposes only.
        logger.info("Member updated state.")

        # Return the validated results.
        return validated_data
