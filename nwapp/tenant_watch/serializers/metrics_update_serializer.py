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
    Watch, WatchMetric, WatchAddress, WatchMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)
from tenant_watch.tasks import process_watch_with_slug_func


logger = logging.getLogger(__name__)


class WatchMetricsUpdateSerializer(serializers.Serializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True, required=False,)
    how_did_you_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )
    how_did_you_hear_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    expectation = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=ExpectationItem.objects.all()
    )
    expectation_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    meaning = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=MeaningItem.objects.all()
    )
    meaning_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    gender = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    willing_to_volunteer = serializers.IntegerField()
    another_household_watch_registered = serializers.BooleanField()
    year_of_birth = serializers.IntegerField()
    total_household_count = serializers.IntegerField(required=False, allow_null=True,)
    under_18_years_household_count = serializers.IntegerField(required=False, allow_null=True,)
    organization_employee_count = serializers.IntegerField(required=False, allow_null=True,)
    organization_founding_year = serializers.IntegerField(required=False, allow_null=True,)

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        # DEVELOPERS NOTE:
        # (1) The body of the metrics data.
        instance.how_did_you_hear = validated_data.get('how_did_you_hear')
        instance.how_did_you_hear_other = validated_data.get('how_did_you_hear_other', None)
        instance.expectation = validated_data.get('expectation')
        instance.expectation_other = validated_data.get('expectation_other', None)
        instance.meaning = validated_data.get('meaning')
        instance.meaning_other = validated_data.get('meaning_other', None)
        instance.gender = validated_data.get('gender')
        instance.willing_to_volunteer = validated_data.get('willing_to_volunteer')
        instance.year_of_birth = validated_data.get('year_of_birth')

        # DEVELOPERS NOTE:
        # (1) Modified household statistics dependent on whether the household
        #     watch was registered or not.
        another_household_watch_registered = validated_data.get('another_household_watch_registered')
        instance.another_household_watch_registered = another_household_watch_registered
        if another_household_watch_registered:
            instance.total_household_count = None
            instance.under_18_years_household_count = None
        else:
            instance.total_household_count = validated_data.get('total_household_count')
            instance.under_18_years_household_count = validated_data.get('under_18_years_household_count')

        # DEVELOPERS NOTE:
        # (1) Non-business watchs cannot have the following fields set,
        #     therefore we need to remove the data if the user submits them.
        if instance.watch.type_of != Watch.MEMBER_TYPE_OF.BUSINESS:
            organization_employee_count = None
            organization_founding_year = None
        else:
            instance.organization_employee_count = validated_data.get('organization_employee_count')
            instance.organization_founding_year = validated_data.get('organization_founding_year')

        # DEVELOPERS NOTE:
        # (1) Update the `last_modified` fields from the context.
        request = self.context.get('request')
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable
        instance.save()
        logger.info("Updated watch metrics.")

        '''
        Run in the background the code which will `process` the newly created
        watch object.
        '''
        django_rq.enqueue(
            process_watch_with_slug_func,
            request.tenant.schema_name,
            instance.watch.user.slug
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
