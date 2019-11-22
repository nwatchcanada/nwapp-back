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

from tenant_foundation.models import MeaningItem


class MeaningItemListCreateSerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[
            UniqueValidator(
                queryset=MeaningItem.objects.all(),
            )
        ],
    )
    class Meta:
        model = MeaningItem
        fields = (
            'id',
            'text',
            'sort_number',
            'is_for_associate',
            'is_for_customer',
            'is_for_staff',
            'is_for_partner',
            'is_archived',
        )
