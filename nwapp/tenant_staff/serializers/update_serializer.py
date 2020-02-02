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
    Staff, StaffContact, StaffAddress, StaffMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)


logger = logging.getLogger(__name__)


class StaffUpdateSerializer(serializers.Serializer):
    # ------ MEMBER ------ #

    type_of = serializers.IntegerField(write_only=True,)

    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.IntegerField(write_only=True,)
    is_ok_to_text = serializers.IntegerField(write_only=True,)
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[
            UniqueValidator(queryset=StaffContact.objects.all()),
        ],
        write_only=True,
    )
    organization_type_of = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )
    first_name = serializers.CharField(write_only=True,)
    last_name = serializers.CharField(write_only=True,)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=SharedUser.objects.all()),
        ],
        write_only=True,
    )
    primary_phone = E164PhoneNumberField(write_only=True,)
    secondary_phone = E164PhoneNumberField(
        allow_null=True,
        required=False,
        write_only=True,
    )

    # ------ MEMBER ADDRESS ------ #

    country = serializers.CharField(write_only=True,)
    region = serializers.CharField(write_only=True,)
    locality = serializers.CharField(write_only=True,)
    street_number = serializers.CharField(write_only=True,)
    street_name =serializers.CharField(write_only=True,)
    apartment_unit = serializers.CharField(write_only=True,)
    street_type = serializers.CharField(write_only=True,)
    street_type_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    street_direction = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    postal_code = serializers.CharField(write_only=True,)

    # ------ MEMBER WATCH ------ #

    #TODO: IMPLEMENT FIELDS.

    # ------ MEMBER METRICS ------ #

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    how_did_you_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all(),
        write_only=True,
    )
    how_did_you_hear_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    expectation = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=ExpectationItem.objects.all(),
        write_only=True,
    )
    expectation_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    meaning = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=MeaningItem.objects.all(),
        write_only=True,
    )
    meaning_other = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
    )
    gender = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        write_only=True,
    )
    willing_to_volunteer = serializers.IntegerField(write_only=True,)
    another_household_staff_registered = serializers.BooleanField(write_only=True,)
    year_of_birth = serializers.IntegerField(write_only=True,)
    total_household_count = serializers.IntegerField(write_only=True,)
    over_18_years_household_count = serializers.IntegerField(write_only=True,)
    organization_employee_count = serializers.IntegerField(write_only=True,)
    organization_founding_year = serializers.IntegerField(write_only=True,)
    organization_type_of = serializers.IntegerField(write_only=True,)

    def update(self, instance, validated_data):
        return validated_data
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')
        print("---->>>>", request)

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
        # # Attach the user to the `Staff` group.
        # user.groups.add(MEMBER_GROUP_ID)
        # logger.info("Shared user assigned as staff.")
        #
        # staff = Staff.objects.create(
        #     user=user,
        #     type_of=type_of,
        #     created_by=request.user,
        #     created_from=request.client_ip,
        #     created_from_is_public=request.client_ip_is_routable,
        #     last_modified_by=request.user,
        #     last_modified_from=request.client_ip,
        #     last_modified_from_is_public=request.client_ip_is_routable,
        # )
        # logger.info("Updated staff.")
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
        # staff_contact = StaffContact.objects.create(
        #     staff=staff,
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
        # logger.info("Updated staff contact.")
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
        # staff_address = StaffAddress.objects.create(
        #     staff=staff,
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
        # logger.info("Updated staff address.")
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
        # another_household_staff_registered = validated_data.get('another_household_staff_registered')
        # year_of_birth = validated_data.get('year_of_birth')
        # total_household_count = validated_data.get('total_household_count')
        # over_18_years_household_count = validated_data.get('over_18_years_household_count')
        # organization_employee_count = validated_data.get('organization_employee_count')
        # organization_founding_year = validated_data.get('organization_founding_year')
        #
        # staff_metric = StaffMetric.objects.create(
        #     staff=staff,
        #     how_did_you_hear=how_did_you_hear,
        #     how_did_you_hear_other=how_did_you_hear_other,
        #     expectation=expectation,
        #     expectation_other=expectation_other,
        #     meaning=meaning,
        #     meaning_other=meaning_other,
        #     gender=gender,
        #     willing_to_volunteer=willing_to_volunteer,
        #     another_household_staff_registered=another_household_staff_registered,
        #     year_of_birth=year_of_birth,
        #     total_household_count=total_household_count,
        #     over_18_years_household_count=over_18_years_household_count,
        #     organization_employee_count=organization_employee_count,
        #     organization_founding_year=organization_founding_year,
        # )
        # logger.info("Updated staff metric.")
        #
        # # Attached our tags.
        # tags = validated_data.get('tags', None)
        # if tags is not None:
        #     if len(tags) > 0:
        #         staff_metric.tags.set(tags)
        #         logger.info("Attached tag to staff metric.")
        #
        # return staff

        raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
            "error": "Terminating for debugging purposes only."
        })

        logger.info("Updated area coordinator.")

        return staff
