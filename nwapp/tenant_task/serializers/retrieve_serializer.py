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
from shared_foundation.models import SharedUser
# from tenant_foundation.constants import *
from tenant_foundation.models import (
    TaskItem
)


logger = logging.getLogger(__name__)


class TaskItemRetrieveSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    type_of_label = serializers.CharField(read_only=True, source="get_type_of_label",)
    description = serializers.CharField(read_only=True, source="get_description",)
    due_date = serializers.DateField(read_only=True,)
    district = serializers.SlugField(read_only=True, source="district.slug",)
    watch = serializers.SlugField(read_only=True, source="watch.slug",)
    staff = serializers.SlugField(read_only=True, source="staff.slug",)
    created_at = serializers.DateField(read_only=True,)
    created_by = serializers.SlugField(read_only=True, source="created_by.slug",)
    last_modified_at = serializers.DateField(read_only=True,)
    last_modified_by = serializers.SlugField(read_only=True, source="last_modified_by.slug",)
