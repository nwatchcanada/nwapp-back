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
from tenant_foundation.constants import *
from tenant_foundation.models import (
    # Associate,
    PrivateFileUpload,
    Tag
)


class PrivateFileUploadRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.SlugField(required=True,)
    file_url = serializers.FileField(
        read_only=True,
        max_length=None,
        use_url=True,
        source="data_file"
    )
    title = serializers.CharField(required=True, allow_null=False,)
    description = serializers.CharField(required=True, allow_null=False,)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)
    is_archived = serializers.BooleanField(required=True,)
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)

    # Meta Information.
    class Meta:
        model = PrivateFileUpload
        fields = (
            'id',
            'file_url',
            'title',
            'description',
            'tags',
            'is_archived',
            'created_at',
            'user',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'user',
            'last_modified_by',
            'created_by',
        )
        return queryset
