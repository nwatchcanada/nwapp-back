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
from tenant_foundation.models import Watch, Tag, StreetAddressRange
from tenant_watch.serializers.street_membership_serializers import (
    StreetAddressRangeCreateSerializer,
    StreetAddressRangeUpdateSerializer
)


logger = logging.getLogger(__name__)



class WatchStreetMembershipUpdateSerializer(serializers.Serializer):
    street_membership = serializers.JSONField(required=True, write_only=True,)

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        street_membership = validated_data.get('street_membership')

        # # For debugging purposes only.
        # print(street_membership)

        # Iterate through all the street addresses and process.
        for data in street_membership:
            try:
                street_membership_slug = data['slug']
                obj = StreetAddressRange.objects.get(slug=street_membership_slug)
                s = StreetAddressRangeUpdateSerializer(
                    obj=obj,
                    data=data,
                    context={
                        'request': request,
                        'watch': instance,
                    },
                    many=False,
                );
                s.is_valid(raise_exception=True)
                s.save()
            except Exception as e:
                # print(e)
                s = StreetAddressRangeCreateSerializer(
                    data=data,
                    context={
                        'request': request,
                        'watch': instance,
                    },
                    many=False,
                );
                s.is_valid(raise_exception=True)
                s.save()

        #TODO: IMPLEMENT DELETING ITEMS NOT INCLUDED IN THE ARRAY.

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Updated watch street membership.")
        return instance
