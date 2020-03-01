# -*- coding: utf-8 -*-
import logging
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

from shared_foundation.utils import get_content_file_from_base64_string
from tenant_foundation.models import Item, ItemType, PrivateImageUpload


logger = logging.getLogger(__name__)


class ItemAuthoritiesUpdateSerializer(serializers.Serializer):

    has_notified_authorities = serializers.BooleanField(
        required=False,
        allow_null=False,
    )
    has_accept_authority_cooperation = serializers.BooleanField(
        required=False,
        allow_null=False,
    )

    def validate_has_accept_authority_cooperation(self, value):
        if not value:
            raise serializers.ValidationError(_("You must accept cooperation with authorities to use our system."))
        return value

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        has_notified_authorities = validated_data.get("has_notified_authorities")
        has_accept_authority_cooperation = validated_data.get('has_accept_authority_cooperation')

        # Save it.
        instance.has_notified_authorities = has_notified_authorities
        instance.has_accept_authority_cooperation = has_accept_authority_cooperation
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()

        # print(validated_data)
        # print(instance.has_notified_authorities)
        # print(instance.has_accept_authority_cooperation)

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
