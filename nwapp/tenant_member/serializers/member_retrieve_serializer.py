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
from shared_foundation.drf.fields import PhoneNumberField
# from tenant_foundation.constants import *
from tenant_foundation.models import (
    Member, MemberContact, MemberAddress, MemberMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)
from tenant_foundation.serializers import TagListCreateSerializer


logger = logging.getLogger(__name__)


class MemberRetrieveSerializer(serializers.Serializer):
    # ------ MEMBER ------ #

    slug = serializers.SlugField(source="user.slug")
    type_of = serializers.IntegerField()

    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.IntegerField(source="contact.is_ok_to_email")
    is_ok_to_text = serializers.IntegerField(source="contact.is_ok_to_text")
    organization_name = serializers.CharField(source="contact.organization_name")
    organization_type_of = serializers.IntegerField(source="contact.organization_type_of")
    first_name = serializers.CharField(source="contact.first_name")
    last_name = serializers.CharField(source="contact.last_name")
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="contact.email")
    primary_phone = PhoneNumberField(source="contact.primary_phone")
    e164_primary_phone = serializers.SerializerMethodField()
    secondary_phone = PhoneNumberField(source="contact.secondary_phone")
    e164_secondary_phone = serializers.SerializerMethodField()

    # ------ MEMBER ADDRESS ------ #

    country = serializers.CharField(source="address.country")
    region = serializers.CharField(source="address.region")
    locality = serializers.CharField(source="address.locality")
    street_number = serializers.CharField(source="address.street_number")
    street_name =serializers.CharField(source="address.street_name")
    apartment_unit = serializers.CharField(source="address.apartment_unit")
    street_type = serializers.CharField(source="address.street_type")
    street_type_other = serializers.CharField(source="address.street_type_other")
    street_direction = serializers.CharField(source="address.street_direction")
    postal_code = serializers.CharField(source="address.postal_code")
    address = serializers.CharField(source="address.street_address")
    google_maps_url = serializers.URLField(source="address.google_maps_url")

    # ------ MEMBER WATCH ------ #

    #TODO: IMPLEMENT FIELDS.

    # ------ MEMBER METRICS ------ #

    tags = TagListCreateSerializer(source="metric.tags", many=True,)
    how_did_you_hear = serializers.PrimaryKeyRelatedField(
        source="metric.how_did_you_hear",
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )
    how_did_you_hear_other = serializers.CharField(source="metric.how_did_you_hear_other", required=False, allow_null=True, allow_blank=True,)
    expectation = serializers.PrimaryKeyRelatedField(
        source="metric.expectation",
        many=False,
        required=True,
        allow_null=False,
        queryset=ExpectationItem.objects.all()
    )
    expectation_other = serializers.CharField(source="metric.expectation_other", required=False, allow_null=True, allow_blank=True,)
    meaning = serializers.PrimaryKeyRelatedField(
        source="metric.meaning",
        many=False,
        required=True,
        allow_null=False,
        queryset=MeaningItem.objects.all()
    )
    meaning_other = serializers.CharField(source="metric.meaning_other", required=False, allow_null=True, allow_blank=True,)
    gender = serializers.CharField(source="metric.gender",)
    willing_to_volunteer = serializers.IntegerField(source="metric.willing_to_volunteer",)
    another_household_member_registered = serializers.BooleanField(source="metric.another_household_member_registered",)
    year_of_birth = serializers.IntegerField(source="metric.year_of_birth",)
    total_household_count = serializers.IntegerField(source="metric.total_household_count",)
    under_18_years_household_count = serializers.IntegerField(source="metric.under_18_years_household_count",)
    organization_employee_count = serializers.IntegerField(source="metric.organization_employee_count",)
    organization_founding_year = serializers.IntegerField(source="metric.organization_founding_year",)

    def get_e164_primary_phone(self, obj):
        """
        Converts the "PhoneNumber" object into a "E164" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.contact.primary_phone:
                return phonenumbers.format_number(obj.contact.primary_phone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            print(e)
            return None

    def get_e164_secondary_phone(self, obj):
        """
        Converts the "PhoneNumber" object into a "E164" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.contact.secondary_phone:
                return phonenumbers.format_number(obj.contact.secondary_phone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            print(e)
            return None

    def get_full_name(self, obj):
        try:
            return obj.contact.first_name + " " + obj.contact.last_name
        except Exception as e:
            print(e)
            return None
