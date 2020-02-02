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
# from tenant_foundation.constants import *
from tenant_foundation.models import (
    Member, MemberContact, MemberAddress, MemberMetric,
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)
from tenant_foundation.serializers import TagListCreateSerializer


logger = logging.getLogger(__name__)


class MemberRetrieveSerializer(serializers.Serializer):
    # ------ MEMBER ------ #

    slug = serializers.SlugField(source="user.slug", read_only=True,)
    type_of = serializers.IntegerField(read_only=True,)
    type_of_label = serializers.CharField(source="get_pretty_type_of", read_only=True,)
    avatar_url = serializers.SerializerMethodField()
    state = serializers.CharField(read_only=True,)
    role_id = serializers.IntegerField(source="user.role_id", read_only=True,)

    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.IntegerField(source="contact.is_ok_to_email", read_only=True,)
    is_ok_to_text = serializers.IntegerField(source="contact.is_ok_to_text", read_only=True,)
    organization_name = serializers.CharField(source="contact.organization_name", read_only=True,)
    organization_type_of = serializers.IntegerField(source="contact.organization_type_of", read_only=True,)
    first_name = serializers.CharField(source="contact.first_name", read_only=True,)
    last_name = serializers.CharField(source="contact.last_name", read_only=True,)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="contact.email", read_only=True,)
    primary_phone_e164 = E164PhoneNumberField(source="contact.primary_phone", read_only=True,)
    primary_phone_national = NationalPhoneNumberField(source="contact.primary_phone", read_only=True,)
    secondary_phone_e164 = E164PhoneNumberField(source="contact.secondary_phone", read_only=True,)
    secondary_phone_national = NationalPhoneNumberField(source="contact.secondary_phone", read_only=True,)

    # ------ MEMBER ADDRESS ------ #

    country = serializers.CharField(source="address.country", read_only=True,)
    region = serializers.CharField(source="address.region", read_only=True,)
    locality = serializers.CharField(source="address.locality", read_only=True,)
    street_number = serializers.CharField(source="address.street_number", read_only=True,)
    street_name =serializers.CharField(source="address.street_name", read_only=True,)
    apartment_unit = serializers.CharField(source="address.apartment_unit", read_only=True,)
    street_type = serializers.IntegerField(source="address.street_type", read_only=True,)
    street_type_other = serializers.CharField(source="address.street_type_other", read_only=True,)
    street_direction = serializers.IntegerField(source="address.street_direction", read_only=True,)
    postal_code = serializers.CharField(source="address.postal_code", read_only=True,)
    address = serializers.CharField(source="address.street_address", read_only=True,)
    google_maps_url = serializers.URLField(source="address.google_maps_url", read_only=True,)

    # ------ MEMBER WATCH ------ #

    watch_name = serializers.CharField(source="watch.name", read_only=True,)
    watch_slug = serializers.SlugField(source="watch.slug", read_only=True,)
    watch_type_of = serializers.IntegerField(source="watch.type_of", read_only=True,)

    # ------ MEMBER METRICS ------ #

    tags = TagListCreateSerializer(source="metric.tags", many=True, read_only=True,)
    how_did_you_hear = serializers.PrimaryKeyRelatedField(
        source="metric.how_did_you_hear",
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )
    how_did_you_hear_other = serializers.CharField(
        source="metric.how_did_you_hear_other", required=False, allow_null=True, allow_blank=True,)
    how_did_you_hear_label = serializers.CharField(
        source="metric.how_did_you_hear.text", allow_null=True, read_only=True,)
    expectation = serializers.PrimaryKeyRelatedField(
        source="metric.expectation",
        many=False,
        required=True,
        allow_null=False,
        queryset=ExpectationItem.objects.all()
    )
    expectation_other = serializers.CharField(
        source="metric.expectation_other", required=False, allow_null=True, allow_blank=True,)
    expectation_label = serializers.CharField(
        source="metric.expectation.text", allow_null=True, read_only=True,)
    meaning = serializers.PrimaryKeyRelatedField(
        source="metric.meaning",
        many=False,
        required=True,
        allow_null=False,
        queryset=MeaningItem.objects.all()
    )
    meaning_other = serializers.CharField(source="metric.meaning_other", allow_null=True, allow_blank=True, read_only=True,)
    meaning_label = serializers.CharField(source="metric.meaning.text", allow_null=True, read_only=True,)
    gender = serializers.IntegerField(source="metric.gender", read_only=True,)
    gender_label = serializers.CharField(source="metric.get_pretty_gender", read_only=True,)
    willing_to_volunteer = serializers.IntegerField(source="metric.willing_to_volunteer", read_only=True,)
    willing_to_volunteer_label = serializers.CharField(source="metric.get_pretty_willing_to_volunteer", read_only=True,)
    another_household_member_registered = serializers.BooleanField(source="metric.another_household_member_registered", read_only=True,)
    year_of_birth = serializers.IntegerField(source="metric.year_of_birth", read_only=True,)
    total_household_count = serializers.IntegerField(source="metric.total_household_count", read_only=True,)
    under_18_years_household_count = serializers.IntegerField(source="metric.under_18_years_household_count", read_only=True,)
    organization_employee_count = serializers.IntegerField(source="metric.organization_employee_count", read_only=True,)
    organization_founding_year = serializers.IntegerField(source="metric.organization_founding_year", read_only=True,)

    # ------ AUDITING ------ #

    created_by = serializers.CharField(source="created_by.get_full_name", allow_null=True, read_only=True,)
    last_modified_by = serializers.CharField(source="last_modified_by.get_full_name", allow_null=True, read_only=True,)

    # ------ FUNCTIONS ------ #

    def get_full_name(self, obj):
        try:
            return obj.contact.first_name + " " + obj.contact.last_name
        except Exception as e:
            print(e)
            return None

    def get_avatar_url(self, obj):
        try:
            return obj.avatar_image.image_file.url
        except Exception as e:
            return None
