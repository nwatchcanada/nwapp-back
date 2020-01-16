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
from tenant_foundation.models import District


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
    # logo_image

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

        district = District.objects.create(
            type_of=type_of,
            description=description,
            name=name,
            counselor_name=counselor_name,
            counselor_email=counselor_email,
            counselor_phone=counselor_phone,
            website_url=website_url,
        )

        logger.info("New district was been created.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return district
