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

from shared_foundation.drf.fields import E164PhoneNumberField, NationalPhoneNumberField
# from tenant_foundation.constants import *
from tenant_foundation.models import TaskItem


logger = logging.getLogger(__name__)


class TaskItemListSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True,)
    state = serializers.IntegerField(read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    # type_of_label = serializers.CharField(read_only=True, source="get_type_of_label",)
    due_date = serializers.DateField(read_only=True,)

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'created_by',
            'last_modified_by'
        )
        return queryset
