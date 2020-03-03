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
    Item,
    ItemComment,
)


logger = logging.getLogger(__name__)


class ItemArchiveOperationSerializer(serializers.Serializer):
    item = serializers.SlugField(write_only=True, required=True)
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
        slug = validated_data.get('item')
        item = Item.objects.select_for_update().get(slug=slug)
        request = self.context.get('request')
        state = validated_data.get('state')
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
        ItemComment.objects.create(
            item=item,
            comment=comment_obj,
        )
        # For debugging purposes only.
        logger.info("Item comment created.")

        #-------------------------#
        # Update item object. #
        #-------------------------#
        item.state = state
        item.deactivation_reason = deactivation_reason
        item.deactivation_reason_other = deactivation_reason_other
        item.last_modified_by = request.user
        item.last_modified_from = request.client_ip
        item.last_modified_from_is_public = request.client_ip_is_routable
        item.save()

        # For debugging purposes only.
        logger.info("Item updated state.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        # Return the validated results.
        return item
