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
    Watch,
    WatchComment,
)


logger = logging.getLogger(__name__)


class WatchArchiveOperationSerializer(serializers.Serializer):
    watch = serializers.SlugField(write_only=True, required=True)
    is_archived = serializers.BooleanField(required=True,)
    deactivation_reason = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=Watch.DEACTIVATION_REASON_CHOICES
    )
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
        slug = validated_data.get('watch')
        watch = Watch.objects.select_for_update().get(slug=slug)
        request = self.context.get('request')
        is_archived = validated_data.get('is_archived')
        deactivation_reason = validated_data.get('deactivation_reason', None)
        deactivation_reason_other = validated_data.get('deactivation_reason_other', None)
        comment_text = validated_data.get('comment')

        #------------------------------------------#
        # Create any comments explaining decision. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            text = comment_text,
            created_by = request.user,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable,
            last_modified_by = request.user,
            last_modified_from = request.client_ip,
            last_modified_from_is_public = request.client_ip_is_routable,
        )
        WatchComment.objects.create(
            watch=watch,
            comment=comment_obj,
        )
        # For debugging purposes only.
        logger.info("Watch comment created.")

        #-------------------------#
        # Update watch object. #
        #-------------------------#
        if watch.state == Watch.STATE.INACTIVE:
            watch.state = Watch.STATE.ACTIVE
        else:
            watch.state = Watch.STATE.INACTIVE
        watch.deactivation_reason = deactivation_reason
        watch.deactivation_reason_other = deactivation_reason_other
        watch.last_modified_by = request.user
        watch.last_modified_from = request.client_ip
        watch.last_modified_from_is_public = request.client_ip_is_routable
        watch.save()

        # For debugging purposes only.
        logger.info("Watch updated `is_archived` value.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        # Return the validated results.
        return validated_data
