# -*- coding: utf-8 -*-
import logging
import phonenumbers
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
from shared_foundation.models import SharedUser
from shared_foundation.drf.fields import E164PhoneNumberField
# from tenant_foundation.constants import *
from tenant_foundation.models import Watch, Tag, District


logger = logging.getLogger(__name__)


class WatchInformationUpdateSerializer(serializers.Serializer):
    type_of = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_null=True,
        required=False,
    )
    name = serializers.CharField()
    description = serializers.CharField()
    district = serializers.SlugField()
    is_virtual = serializers.BooleanField(allow_null=True,)

    def validate_district(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not District.objects.filter(slug=value).exists():
            raise serializers.ValidationError("District does not exist")
        return value

    def update(self, instance, validated_data):
        # Get our data and update our model.
        request = self.context.get('request')
        instance.type_of = validated_data.get('type_of')
        instance.name = validated_data.get('name')
        instance.description = validated_data.get('description')
        district_slug = validated_data.get('district')
        instance.district = District.objects.get(slug=district_slug)
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable
        is_virtual = validated_data.get('is_virtual', False)
        if is_virtual == None or is_virtual == "":
            instance.is_virtual = False
        else:
            instance.is_virtual = is_virtual
        instance.save()
        logger.info("Updated watch.")

        # Attached our tags.
        tags = validated_data.get('tags')
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)
                logger.info("Attached tag to watch.")

        # Return the updated instance.
        return instance
