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
from shared_foundation.utils import (
    get_point_from_arr,
    get_polygon_from_multi_arr
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import Watch


logger = logging.getLogger(__name__)


class WatchBoundaryOperationSerializer(serializers.Serializer):
    watch_zoom = serializers.IntegerField(write_only=True, required=True,)
    watch_position = serializers.JSONField(write_only=True, required=True,)
    watch_polygon = serializers.JSONField(write_only=True, required=True,)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.boundry_zoom = validated_data.get('watch_zoom')
        instance.boundry_position = get_point_from_arr(validated_data.get('watch_position'))
        instance.boundry_polygon = get_polygon_from_multi_arr(validated_data.get('watch_polygon'))
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable
        instance.save()
        logger.info("New watch was been updated.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
