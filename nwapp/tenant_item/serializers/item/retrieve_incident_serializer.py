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

from tenant_foundation.models import Item, ItemType


logger = logging.getLogger(__name__)


class IncidentItemRetrieveSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    # # --- COMMON --- #
    # type_of = serializers.IntegerField(
    #     required=True,
    #     allow_null=False,
    # )
    # category = serializers.SlugField(
    #     required=True,
    #     allow_null=False,
    # )
    #
    # # --- EVENT --- #
    # start_date_time = serializers.DateTimeField(
    #     required=False,
    #     allow_null=False,
    # )
    # is_all_day_event = serializers.BooleanField(
    #     required=False,
    #     allow_null=False,
    # )
    # finish_date_time = serializers.DateTimeField(
    #     required=False,
    #     allow_null=False,
    # )
    # title = serializers.CharField(
    #     required=False,
    #     allow_null=True,
    # )
    # description = serializers.CharField(
    #     required=False,
    #     allow_null=True,
    # )
    # #TODO: LOGO / GALLERY
    # external_url = serializers.URLField(
    #     required=False,
    #     allow_null=True,
    # )
    # shown_to_whom = serializers.IntegerField(
    #     required=False,
    #     allow_null=True,
    # )
    # can_be_posted_on_social_media = serializers.BooleanField(
    #     required=False,
    #     allow_null=True,
    # )
