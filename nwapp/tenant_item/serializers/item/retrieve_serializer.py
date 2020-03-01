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
from tenant_private_image_upload.serializers import PrivateImageUploadRetrieveSerializer
from tenant_private_file_upload.serializers import PrivateFileUploadRetrieveSerializer


logger = logging.getLogger(__name__)


class ItemRetrieveSerializer(serializers.Serializer):

    # --- ALL --- #

    slug = serializers.SlugField(read_only=True,)
    state = serializers.CharField(read_only=True,)
    type_of_category = serializers.IntegerField(read_only=True,source="type_of.category",)
    type_of_category_label = serializers.CharField(read_only=True,source="type_of.get_category_label",)
    type_of_text = serializers.CharField(read_only=True,source="type_of.text",)
    type_of_slug = serializers.CharField(read_only=True,source="type_of.slug",)
    description = serializers.CharField(read_only=True,)
    is_archived = serializers.BooleanField(read_only=True,)
    event_logo_image = PrivateImageUploadRetrieveSerializer(
        read_only=True,
        many=False,
        allow_null=True,
    )
    photos = PrivateImageUploadRetrieveSerializer(
        read_only=True,
        many=True,
        allow_null=True,
        source="private_image_uploads",
    )

    # --- EVENT --- #

    start_date_time = serializers.DateTimeField(
        required=False,
        allow_null=False,
    )
    is_all_day_event = serializers.BooleanField(
        required=False,
        allow_null=False,
    )
    finish_date_time = serializers.DateTimeField(
        required=False,
        allow_null=False,
    )
    title = serializers.CharField( # Event / Incident / Concern
        required=False,
        allow_null=True,
    )
    external_url = serializers.URLField(
        required=False,
        allow_null=False,
    )
    shown_to_whom = serializers.IntegerField(
        required=False,
        allow_null=False,
    )
    can_be_posted_on_social_media = serializers.IntegerField(
        required=False,
        allow_null=False,
    )
    # event_logo_image #TODO: IMPLEMENT

    # --- INCIDENT / CONCERN --- #

    has_notified_authorities = serializers.BooleanField(
        required=False,
        allow_null=False,
    )
    has_accept_authority_cooperation = serializers.BooleanField(
        required=False,
        allow_null=False,
    )
    date = serializers.DateTimeField( #DateTimeField
        required=False,
        allow_null=False,
    )
    location = serializers.CharField( # Event / Incident / Concern
        required=False,
        allow_null=True,
    )

    # --- COMMUNITY NEWS --- #

    who_news_for = serializers.IntegerField(
        required=False,
        allow_null=False,
    )
    who_news_for_label = serializers.CharField(
        required=False,
        allow_null=False,
        source="get_who_news_for_label"
    )

    # --- RESOURCE --- #

    format_type = serializers.IntegerField(
        required=False,
        allow_null=False,
    )
    embed_code = serializers.CharField(
        required=False,
        allow_null=False,
    )
    resource_image  = PrivateImageUploadRetrieveSerializer(
        read_only=True,
        many=False,
        allow_null=True,
    )
    resource_file = PrivateFileUploadRetrieveSerializer(
        read_only=True,
        many=False,
        allow_null=True,
    )
