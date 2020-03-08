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
    slug = serializers.SlugField(read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    # type_of_label = serializers.CharField(source="get_pretty_type_of", read_only=True,)
