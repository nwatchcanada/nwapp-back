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
from tenant_foundation.models import (
    Member, MemberContact, MemberAddress, MemberMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem, Watch
)


logger = logging.getLogger(__name__)


class MemberWatchUpdateSerializer(serializers.Serializer):
    watch = serializers.SlugField(required=True, write_only=True,)

    def validate_watch(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not Watch.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Watch does not exist")
        return value

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        # Get our inputs.
        request = self.context.get('request')
        watch_slug = validated_data.get('watch')
        watch = Watch.objects.get(slug=watch_slug)

        # Update our model.
        instance.watch = watch
        instance.last_modified_by=request.user
        instance.last_modified_from=request.client_ip
        instance.last_modified_from_is_public=request.client_ip_is_routable
        instance.save()

        # Return our modified instances.
        return instance
