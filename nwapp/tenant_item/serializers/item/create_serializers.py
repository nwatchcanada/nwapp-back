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


class ItemCreateSerializer(serializers.Serializer):
    # --- COMMON --- #
    type_of = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    category = serializers.SlugField(
        required=True,
        allow_null=False,
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
    title = serializers.CharField(
        required=False,
        allow_null=True,
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
    )
    #TODO: LOGO / GALLERY
    external_url = serializers.URLField(
        required=False,
        allow_null=True,
    )
    shown_to_whom = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    can_be_posted_on_social_media = serializers.BooleanField(
        required=False,
        allow_null=True,
    )

    def validate_category(self, value):
        """
        Add extra validation.
        (1) Lookup `ItemType` based on `category`.
        (2) Lookup `ItemType` based on `slug`.
        """
        type_of = self.context.get("type_of")
        does_exist = ItemType.objects.filter(
            slug=value,
            category=type_of
        ).exists()
        if does_exist:
            return value
        else:
            raise serializers.ValidationError(_("Item type does not exist."))

    def validate_start_date_time(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing start date / time."))

    def validate_finish_date_time(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing finish date / time."))

    def validate_title(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing title."))

    def validate_description(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing description."))

    def validate_shown_to_whom(self, value):
        type_of = self.context.get("type_of")
        if type_of == ItemType.CATEGORY.EVENT and value != "" and value != None:
            return value
        else:
            raise serializers.ValidationError(_("Missing description."))

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get("request")
        type_of = self.context.get("type_of")
        category = validated_data.get('category')
        # text = validated_data.get('text')
        # description = validated_data.get('description')
        #
        # # Create the district.
        # item_type = Item.objects.create(
        #     description=description,
        #     text=text,
        #     category=category,
        #     created_by = request.user,
        #     created_from = request.client_ip,
        #     created_from_is_public = request.client_ip_is_routable,
        #     last_modified_by = request.user,
        #     last_modified_from = request.client_ip,
        #     last_modified_from_is_public = request.client_ip_is_routable,
        # )
        #
        # logger.info("New item_type was been created.")
        #
        # # print(private_file)
        # # print("\n")

        raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
            "error": "Terminating for debugging purposes only."
        })
        return None

        # return item_type
