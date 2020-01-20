# -*- coding: utf-8 -*-
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

from tenant_foundation.models import HowHearAboutUsItem


class HowHearAboutUsItemRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[
            UniqueValidator(
                queryset=HowHearAboutUsItem.objects.all(),
            )
        ],
    )

    # ------ AUDITING ------ #
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)
    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_at = serializers.DateTimeField(read_only=True, allow_null=False,)

    class Meta:
        model = HowHearAboutUsItem
        fields = (
            'id',
            'text',
            'sort_number',
            'is_for_associate',
            'is_for_customer',
            'is_for_staff',
            'is_for_partner',
            'is_archived',
            'created_at',
            'created_by',
            'last_modified_at',
            'last_modified_by'
        )
