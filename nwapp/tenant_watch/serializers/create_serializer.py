# -*- coding: utf-8 -*-
import logging
import django_rq
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.drf.fields import E164PhoneNumberField
from shared_foundation.models import SharedUser, SharedGroup
# from tenant_foundation.constants import *
from tenant_foundation.models import Watch, Tag
from tenant_watch.tasks import process_watch_with_slug_func


logger = logging.getLogger(__name__)

# associate: localStorage.getItem('nwapp-watch-associate'),
# district: localStorage.getItem('nwapp-watch-district'),
# districtOption: localStorageGetObjectItem('nwapp-watch-districtOption'),
# streetMembership: localStorageGetArrayItem('nwapp-watch-streetMembership'),


class WatchCreateSerializer(serializers.Serializer):

    type_of = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_null=True,
        required=False,
    )
    name = serializers.CharField()
    description = serializers.CharField()

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        name = validated_data.get('name')
        description = validated_data.get('description')

        # # Attached our tags.
        # tags = validated_data.get('tags', None)
        # if tags is not None:
        #     if len(tags) > 0:
        #         member_metric.tags.set(tags)
        #         logger.info("Attached tag to member metric.")

        # ------ MEMBER ------ #
    #
    #     type_of = validated_data.get('type_of')
    #     first_name = validated_data.get('first_name')
    #     last_name = validated_data.get('last_name')
    #     email = validated_data.get('email')
    #
    #     user = SharedUser.objects.create(
    #         tenant=request.tenant,
    #         first_name=first_name,
    #         last_name=last_name,
    #         email=email,
    #         was_email_activated=True,
    #         is_active=True,
    #     )
    #     logger.info("Created shared user.")
    #
    #     # Attach the user to the `Watch` group.
    #     user.groups.add(SharedGroup.GROUP_MEMBERSHIP.MEMBER)
    #     logger.info("Shared user assigned as watch.")
    #
    #     watch = Watch.objects.create(
    #         user=user,
    #         type_of=type_of,
    #         created_by=request.user,
    #         created_from=request.client_ip,
    #         created_from_is_public=request.client_ip_is_routable,
    #         last_modified_by=request.user,
    #         last_modified_from=request.client_ip,
    #         last_modified_from_is_public=request.client_ip_is_routable,
    #     )
    #     logger.info("Created watch.")
    #
    #     # ------ MEMBER CONTACT ------ #
    #
    #     is_ok_to_email = validated_data.get('is_ok_to_email')
    #     is_ok_to_text = validated_data.get('is_ok_to_text')
    #     organization_name = validated_data.get('organization_name')
    #     organization_type_of = validated_data.get('organization_type_of')
    #     primary_phone = validated_data.get('primary_phone', None)
    #     secondary_phone = validated_data.get('secondary_phone', None)
    #
    #     # DEVELOPERS NOTE:
    #     # (1) Non-business watchs cannot have the following fields set,
    #     #     therefore we need to remove the data if the user submits them.
    #     if type_of != Watch.MEMBER_TYPE_OF.BUSINESS:
    #         organization_name = None
    #         organization_type_of = WatchContact.MEMBER_ORGANIZATION_TYPE_OF.UNSPECIFIED
    #
    #     watch_contact = WatchContact.objects.create(
    #         watch=watch,
    #         is_ok_to_email=is_ok_to_email,
    #         is_ok_to_text=is_ok_to_text,
    #         organization_name=organization_name,
    #         organization_type_of=organization_type_of,
    #         first_name=first_name,
    #         last_name=last_name,
    #         email=email,
    #         primary_phone=primary_phone,
    #         secondary_phone=secondary_phone,
    #         created_by=request.user,
    #         created_from=request.client_ip,
    #         created_from_is_public=request.client_ip_is_routable,
    #         last_modified_by=request.user,
    #         last_modified_from=request.client_ip,
    #         last_modified_from_is_public=request.client_ip_is_routable,
    #     )
    #     logger.info("Created watch contact.")
    #
    #     # ------ MEMBER ADDRESS ------ #
    #
    #     country = validated_data.get('country', None)
    #     region = validated_data.get('region', None)
    #     locality = validated_data.get('locality', None)
    #     street_number = validated_data.get('street_number', None)
    #     street_name = validated_data.get('street_name', None)
    #     apartment_unit = validated_data.get('apartment_unit', None)
    #     street_type = validated_data.get('street_type', None)
    #     street_type_other = validated_data.get('street_type_other', None)
    #     street_direction = validated_data.get('street_direction', WatchAddress.STREET_DIRECTION.NONE)
    #     postal_code = validated_data.get('postal_code', None)
    #     watch_address = WatchAddress.objects.create(
    #         watch=watch,
    #         country=country,
    #         region=region,
    #         locality=locality,
    #         street_number=street_number,
    #         street_name=street_name,
    #         apartment_unit=apartment_unit,
    #         street_type=street_type,
    #         street_type_other=street_type_other,
    #         street_direction=street_direction,
    #         postal_code=postal_code,
    #         created_by=request.user,
    #         created_from=request.client_ip,
    #         created_from_is_public=request.client_ip_is_routable,
    #         last_modified_by=request.user,
    #         last_modified_from=request.client_ip,
    #         last_modified_from_is_public=request.client_ip_is_routable,
    #     )
    #     logger.info("Created watch address.")
    #
    #     # ------ MEMBER METRICS ------ #
    #
    #     how_did_you_hear = validated_data.get('how_did_you_hear')
    #     how_did_you_hear_other = validated_data.get('how_did_you_hear_other', None)
    #     expectation = validated_data.get('expectation')
    #     expectation_other = validated_data.get('expectation_other', None)
    #     meaning = validated_data.get('meaning')
    #     meaning_other = validated_data.get('meaning_other', None)
    #     gender = validated_data.get('gender')
    #     willing_to_volunteer = validated_data.get('willing_to_volunteer')
    #     another_household_watch_registered = validated_data.get('another_household_watch_registered')
    #     year_of_birth = validated_data.get('year_of_birth')
    #     total_household_count = validated_data.get('total_household_count')
    #     under_18_years_household_count = validated_data.get('under_18_years_household_count')
    #     organization_employee_count = validated_data.get('organization_employee_count')
    #     organization_founding_year = validated_data.get('organization_founding_year')
    #
    #     # DEVELOPERS NOTE:
    #     # (1) Non-business watchs cannot have the following fields set,
    #     #     therefore we need to remove the data if the user submits them.
    #     if type_of != Watch.MEMBER_TYPE_OF.BUSINESS:
    #         organization_employee_count = None
    #         organization_founding_year = None
    #
    #     watch_metric = WatchMetric.objects.create(
    #         watch=watch,
    #         how_did_you_hear=how_did_you_hear,
    #         how_did_you_hear_other=how_did_you_hear_other,
    #         expectation=expectation,
    #         expectation_other=expectation_other,
    #         meaning=meaning,
    #         meaning_other=meaning_other,
    #         gender=gender,
    #         willing_to_volunteer=willing_to_volunteer,
    #         another_household_watch_registered=another_household_watch_registered,
    #         year_of_birth=year_of_birth,
    #         total_household_count=total_household_count,
    #         under_18_years_household_count=under_18_years_household_count,
    #         organization_employee_count=organization_employee_count,
    #         organization_founding_year=organization_founding_year,
    #     )
    #     logger.info("Created watch metric.")
    #
    #     # Attached our tags.
    #     tags = validated_data.get('tags', None)
    #     if tags is not None:
    #         if len(tags) > 0:
    #             watch_metric.tags.set(tags)
    #             logger.info("Attached tag to watch metric.")
    #
    #     '''
    #     Run in the background the code which will `process` the newly created
    #     watch object.
    #     '''
    #     django_rq.enqueue(
    #         process_watch_with_slug_func,
    #         request.tenant.schema_name,
    #         watch.user.slug
    #     )
    #
    #     # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
    #     #     "error": "Terminating for debugging purposes only."
    #     # })
    #
    #     return watch
