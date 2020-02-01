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

        # DEVELOPERS NOTE:
        # (1) ARCHIVED ANY RECORDS WHICH NEED TO BE DELETED.
        #
        # The following code will find all the objects which have not been
        # included by the user from the API, thus indicating we are to 'delete'
        # those records.
        target_slugs = instance.street_address_ranges.filter(
            is_archived=False
        ).values_list('slug', flat=True)
        search_slugs = StreetAddressRange.slugs_from_data(street_membership)
        # print("SEARCH SLUGS", search_slugs)
        # print("TARGET SLUGS", target_slugs)
        missing_slugs = StreetAddressRange.missing_slugs(search_slugs, target_slugs)
        # print("MISSING SLUGS", missing_slugs)
        missing_objects = StreetAddressRange.objects.filter(slug__in=missing_slugs)

        # Iterate through all the missing objects and set their status to be
        # archived so we cannot use them again.
        for missing_object in missing_objects.all():
            missing_object.is_archived = True
            missing_object.last_modified_by=request.user
            missing_object.last_modified_from=request.client_ip
            missing_object.last_modified_from_is_public=request.client_ip_is_routable
            missing_object.save()
            # print("ARCHIVED")
            logger.info("Archived watch street membership.")

        # DEVELOPERS NOTES:
        # (1) WE WILL NOW EITHER CREATE OR UPDATE OUR STREET RANGES.
        #
        # Iterate through all the street addresses and process.
        for data in street_membership:
            try:
                street_membership_slug = data['slug']
                obj = StreetAddressRange.objects.get(slug=street_membership_slug)
                s = StreetAddressRangeUpdateSerializer(
                    obj,
                    data=data,
                    context={
                        'request': request,
                        'watch': instance,
                    },
                    many=False,
                );
                s.is_valid(raise_exception=True)
                s.save()
                # print("UPDATED STREET RANGE")
                logger.info("Updated watch street membership.")
            except Exception as e:
                # print("\n\n\n", e, "\n\n\n")
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
                # print("CREATED STREET RANGE")
                logger.info("Created watch street membership.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
