# -*- coding: utf-8 -*-
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
from shared_foundation.drf.fields import E164PhoneNumberField, NationalPhoneNumberField
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_arr_from_point
from tenant_foundation.models import (
    Associate, AssociateContact, AssociateAddress, AssociateMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)
from tenant_foundation.serializers import TagListCreateSerializer
from tenant_associate.serializers.governing_district_retrieve_serializer import GoverningDistrictRetrieveSerializer


logger = logging.getLogger(__name__)


class AssociateRetrieveSerializer(serializers.Serializer):
    # ------ MEMBER ------ #

    slug = serializers.SlugField(source="user.slug", read_only=True,)
    type_of = serializers.IntegerField(source="user.member.type_of", read_only=True,)
    type_of_label = serializers.CharField(source="user.member.get_pretty_type_of", read_only=True,)
    avatar_url = serializers.SerializerMethodField()
    state = serializers.CharField(source="user.member.state", read_only=True,)

    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.IntegerField(source="user.member.contact.is_ok_to_email", read_only=True,)
    is_ok_to_text = serializers.IntegerField(source="user.member.contact.is_ok_to_text", read_only=True,)
    organization_name = serializers.CharField(source="user.member.contact.organization_name", read_only=True, allow_blank=True,)
    organization_type_of = serializers.IntegerField(source="user.member.contact.organization_type_of", read_only=True,)
    first_name = serializers.CharField(source="user.member.contact.first_name", read_only=True,)
    last_name = serializers.CharField(source="user.member.contact.last_name", read_only=True,)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.member.contact.email", read_only=True,)
    primary_phone_e164 = E164PhoneNumberField(source="user.member.contact.primary_phone", read_only=True,)
    primary_phone_national = NationalPhoneNumberField(source="user.member.contact.primary_phone", read_only=True,)
    secondary_phone_e164 = E164PhoneNumberField(source="user.member.contact.secondary_phone", read_only=True,)
    secondary_phone_national = NationalPhoneNumberField(source="user.member.contact.secondary_phone", read_only=True,)

    # ------ MEMBER ADDRESS ------ #

    country = serializers.CharField(source="user.member.address.country", read_only=True,)
    province = serializers.CharField(source="user.member.address.province", read_only=True,)
    city = serializers.CharField(source="user.member.address.city", read_only=True,)
    street_number = serializers.CharField(source="user.member.address.street_number", read_only=True,)
    street_name =serializers.CharField(source="user.member.address.street_name", read_only=True,)
    apartment_unit = serializers.CharField(source="user.member.address.apartment_unit", read_only=True,)
    street_type = serializers.IntegerField(source="user.member.address.street_type", read_only=True,)
    street_type_other = serializers.CharField(source="user.member.address.street_type_other", read_only=True,)
    street_direction = serializers.IntegerField(source="user.member.address.street_direction", read_only=True,)
    postal_code = serializers.CharField(source="user.member.address.postal_code", read_only=True,)
    address = serializers.CharField(source="user.member.address.street_address", read_only=True,)
    google_maps_url = serializers.URLField(source="user.member.address.google_maps_url", read_only=True,)
    position = serializers.SerializerMethodField()

    # ------ MEMBER WATCH ------ #

    #TODO: IMPLEMENT FIELDS.

    # ------ MEMBER METRICS ------ #

    tags = TagListCreateSerializer(source="user.member.metric.tags", many=True, read_only=True,)
    how_did_you_hear = serializers.PrimaryKeyRelatedField(
        source="user.member.metric.how_did_you_hear",
        many=False,
        read_only=True,
        allow_null=False,
    )
    how_did_you_hear_other = serializers.CharField(source="user.member.metric.how_did_you_hear_other", allow_null=True, allow_blank=True, read_only=True,)
    how_did_you_hear_label = serializers.CharField(source="user.member.metric.how_did_you_hear.text", read_only=True, allow_blank=True, allow_null=True,)
    expectation = serializers.PrimaryKeyRelatedField(
        source="user.member.metric.expectation",
        many=False,
        read_only=True,
        allow_null=False,
    )
    expectation_other = serializers.CharField(source="user.member.metric.expectation_other", allow_null=True, allow_blank=True, read_only=True,)
    expectation_label = serializers.CharField(source="user.member.metric.expectation.text", read_only=True, allow_null=True, allow_blank=True, )
    meaning = serializers.PrimaryKeyRelatedField(
        source="user.member.metric.meaning",
        many=False,
        read_only=True,
        allow_null=False,
    )
    meaning_other = serializers.CharField(source="user.member.metric.meaning_other", allow_null=True, allow_blank=True, read_only=True,)
    meaning_label = serializers.CharField(source="user.member.metric.meaning.text", read_only=True, allow_null=True, allow_blank=True,)
    gender = serializers.IntegerField(source="user.member.metric.gender", read_only=True,)
    gender_label = serializers.CharField(source="user.member.metric.get_pretty_gender", read_only=True,)
    willing_to_volunteer = serializers.IntegerField(source="user.member.metric.willing_to_volunteer", read_only=True,)
    willing_to_volunteer_label = serializers.CharField(source="user.member.metric.get_pretty_willing_to_volunteer", read_only=True,)
    another_household_member_registered = serializers.BooleanField(source="user.member.metric.another_household_member_registered", read_only=True,)
    year_of_birth = serializers.IntegerField(source="user.member.metric.year_of_birth", read_only=True,)
    total_household_count = serializers.IntegerField(source="user.member.metric.total_household_count", read_only=True,)
    over_18_years_household_count = serializers.IntegerField(source="user.member.metric.over_18_years_household_count", read_only=True,)
    organization_employee_count = serializers.IntegerField(source="user.member.metric.organization_employee_count", read_only=True,)
    organization_founding_year = serializers.IntegerField(source="user.member.metric.organization_founding_year", read_only=True,)
    governing = serializers.SerializerMethodField()

    # ------ AUDITING ------ #

    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)

    # ------ FUNCTIONS ------ #

    def get_full_name(self, obj):
        try:
            return obj.user.member.contact.first_name + " " + obj.user.member.contact.last_name
        except Exception as e:
            print(e)
            return None

    def get_avatar_url(self, obj):
        try:
            return obj.user.member.avatar_image.image_file.url
        except Exception as e:
            return

    def get_governing(self, obj):
        try:
            s = GoverningDistrictRetrieveSerializer(
               obj.governing.all(),
               many=True,
               context=self.context
            )
            return s.data
        except Exception as e:
            # print("get_governing |", e)
            return None

    def get_position(self, obj):
        return get_arr_from_point(obj.user.member.address.position)
