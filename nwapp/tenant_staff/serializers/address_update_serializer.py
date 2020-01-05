# -*- coding: utf-8 -*-
import django_rq
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
from shared_foundation.drf.fields import E164PhoneNumberField
from shared_foundation.models import SharedUser
# from tenant_foundation.constants import *
from tenant_foundation.models import (
    Staff, StaffContact, StaffAddress, StaffMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)
from tenant_staff.tasks import process_staff_with_slug_func


logger = logging.getLogger(__name__)


class StaffAddressUpdateSerializer(serializers.Serializer):
    # ------ MEMBER ADDRESS ------ #
    country = serializers.CharField()
    region = serializers.CharField()
    locality = serializers.CharField()
    street_number = serializers.CharField()
    street_name =serializers.CharField()
    apartment_unit = serializers.CharField()
    street_type = serializers.ChoiceField(choices=StaffAddress.STREET_TYPE_CHOICES,)
    street_type_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    street_direction = serializers.ChoiceField(choices=StaffAddress.STREET_DIRECTION_CHOICES,)
    postal_code = serializers.CharField()

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        # ------ MEMBER ADDRESS ------ #
        request = self.context.get('request')
        instance.country = validated_data.get('country', None)
        instance.region = validated_data.get('region', None)
        instance.locality = validated_data.get('locality', None)
        instance.street_number = validated_data.get('street_number', None)
        instance.street_name = validated_data.get('street_name', None)
        instance.apartment_unit = validated_data.get('apartment_unit', None)
        instance.street_type = validated_data.get('street_type', None)
        instance.street_type_other = validated_data.get('street_type_other', None)
        instance.street_direction = validated_data.get('street_direction', None)
        instance.postal_code = validated_data.get('postal_code', None)
        instance.save()
        logger.info("Updated staff address.")

        '''
        Run in the background the code which will `process` the newly created
        staff object.
        '''
        django_rq.enqueue(
            process_staff_with_slug_func,
            request.tenant.schema_name,
            instance.staff.user.slug
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
