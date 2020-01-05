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
from tenant_foundation.models import Award


logger = logging.getLogger(__name__)


class AwardRetrieveSerializer(serializers.Serializer):
    user = serializers.SlugField(
        read_only=True,
        source="user.slug",
    )
    type_of = serializers.IntegerField(read_only=True,)
    type_of_other = serializers.CharField(read_only=True,)
    type_of_label = serializers.CharField(read_only=True, source="get_type_of_label")
    description = serializers.CharField(read_only=True, source="get_description")
    icon = serializers.CharField(read_only=True,)
    colour = serializers.CharField(read_only=True,)
    created_at = serializers.DateTimeField(read_only=True,)
    last_modified_at = serializers.DateTimeField(read_only=True,)
    is_archived = serializers.BooleanField(read_only=True,)
    uuid = serializers.UUIDField(read_only=True,)
