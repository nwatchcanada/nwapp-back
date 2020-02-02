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
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)


logger = logging.getLogger(__name__)


class MemberWatchUpdateSerializer(serializers.Serializer):
    watch = serializers.SlugField(required=True,)

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        request = self.context.get('request')
        watch_slug = validated_data.get('watch')
        print("---->>>>", request)
        return instance

        #TODO: IMPLEMENT CODE BELOW.

        # # ------ MEMBER ------ #
        #
        # type_of = validated_data.get('type_of')
        # first_name = validated_data.get('first_name')
        # last_name = validated_data.get('last_name')
        # email = validated_data.get('email')
        #
        # user = SharedUser.objects.create(
        #     tenant=request.tenant,
        #     first_name=first_name,
        #     last_name=last_name,
        #     email=email,
        #     was_email_activated=True,
        #     is_active=True,
        # )
        # logger.info("Updated shared user.")
        #
        # # Attach the user to the `Member` group.
        # user.groups.add(MEMBER_GROUP_ID)
        # logger.info("Shared user assigned as member.")
        #
        # member = Member.objects.create(
        #     user=user,
        #     type_of=type_of,
        #     created_by=request.user,
        #     created_from=request.client_ip,
        #     created_from_is_public=request.client_ip_is_routable,
        #     last_modified_by=request.user,
        #     last_modified_from=request.client_ip,
        #     last_modified_from_is_public=request.client_ip_is_routable,
        # )
        # logger.info("Updated member.")
        #
        # # ------ MEMBER CONTACT ------ #
        #
        # is_ok_to_email = validated_data.get('is_ok_to_email')
        # is_ok_to_text = validated_data.get('is_ok_to_text')
        # organization_name = validated_data.get('organization_name')
        # organization_type_of = validated_data.get('organization_type_of')
        # primary_phone = validated_data.get('primary_phone', None)
        # primary_phone = phonenumbers.parse(primary_phone, "CA")
        # secondary_phone = validated_data.get('secondary_phone', None)
        # if secondary_phone is not None:
        #     secondary_phone = phonenumbers.parse(secondary_phone, "CA")
        #
        # member_contact = MemberContact.objects.create(
        #     member=member,
        #     is_ok_to_email=is_ok_to_email,
        #     is_ok_to_text=is_ok_to_text,
        #     organization_name=organization_name,
        #     organization_type_of=organization_type_of,
        #     first_name=first_name,
        #     last_name=last_name,
        #     email=email,
        #     primary_phone=primary_phone,
        #     secondary_phone=secondary_phone,
        #     created_by=request.user,
        #     created_from=request.client_ip,
        #     created_from_is_public=request.client_ip_is_routable,
        #     last_modified_by=request.user,
        #     last_modified_from=request.client_ip,
        #     last_modified_from_is_public=request.client_ip_is_routable,
        # )
        # logger.info("Updated member contact.")
        #
        # # ------ MEMBER ADDRESS ------ #
        #
        # country = validated_data.get('country', None)
        # region = validated_data.get('region', None)
        # locality = validated_data.get('locality', None)
        # street_number = validated_data.get('street_number', None)
        # street_name = validated_data.get('street_name', None)
        # apartment_unit = validated_data.get('apartment_unit', None)
        # street_type = validated_data.get('street_type', None)
        # street_type_other = validated_data.get('street_type_other', None)
        # street_direction = validated_data.get('street_direction', None)
        # postal_code = validated_data.get('postal_code', None)
        # member_address = MemberAddress.objects.create(
        #     member=member,
        #     country=country,
        #     region=region,
        #     locality=locality,
        #     street_number=street_number,
        #     street_name=street_name,
        #     apartment_unit=apartment_unit,
        #     street_type=street_type,
        #     street_type_other=street_type_other,
        #     street_direction=street_direction,
        #     postal_code=postal_code,
        #     created_by=request.user,
        #     created_from=request.client_ip,
        #     created_from_is_public=request.client_ip_is_routable,
        #     last_modified_by=request.user,
        #     last_modified_from=request.client_ip,
        #     last_modified_from_is_public=request.client_ip_is_routable,
        # )
        # logger.info("Updated member address.")
        #
        # # ------ MEMBER METRICS ------ #
        #
        # how_did_you_hear = validated_data.get('how_did_you_hear')
        # how_did_you_hear_other = validated_data.get('how_did_you_hear_other', None)
        # expectation = validated_data.get('expectation')
        # expectation_other = validated_data.get('expectation', None)
        # meaning = validated_data.get('meaning')
        # meaning_other = validated_data.get('meaning_other', None)
        # gender = validated_data.get('gender')
        # willing_to_volunteer = validated_data.get('willing_to_volunteer')
        # another_household_member_registered = validated_data.get('another_household_member_registered')
        # year_of_birth = validated_data.get('year_of_birth')
        # total_household_count = validated_data.get('total_household_count')
        # under_18_years_household_count = validated_data.get('under_18_years_household_count')
        # organization_employee_count = validated_data.get('organization_employee_count')
        # organization_founding_year = validated_data.get('organization_founding_year')
        #
        # member_metric = MemberMetric.objects.create(
        #     member=member,
        #     how_did_you_hear=how_did_you_hear,
        #     how_did_you_hear_other=how_did_you_hear_other,
        #     expectation=expectation,
        #     expectation_other=expectation_other,
        #     meaning=meaning,
        #     meaning_other=meaning_other,
        #     gender=gender,
        #     willing_to_volunteer=willing_to_volunteer,
        #     another_household_member_registered=another_household_member_registered,
        #     year_of_birth=year_of_birth,
        #     total_household_count=total_household_count,
        #     under_18_years_household_count=under_18_years_household_count,
        #     organization_employee_count=organization_employee_count,
        #     organization_founding_year=organization_founding_year,
        # )
        # logger.info("Updated member metric.")
        #
        # # Attached our tags.
        # tags = validated_data.get('tags', None)
        # if tags is not None:
        #     if len(tags) > 0:
        #         member_metric.tags.set(tags)
        #         logger.info("Attached tag to member metric.")
        #
        # return member
