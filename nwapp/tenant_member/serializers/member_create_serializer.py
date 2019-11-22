# -*- coding: utf-8 -*-
import logging
import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.models import SharedUser
from shared_foundation.drf.fields import PhoneNumberField
# from tenant_foundation.constants import *
from tenant_foundation.models import (
    Member, MemberContact, Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem
)


logger = logging.getLogger(__name__)


class MemberCreateSerializer(serializers.Serializer):
    # ------ MEMBER ------ #

    type_of = serializers.IntegerField()

    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.IntegerField()
    is_ok_to_text = serializers.IntegerField()
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[
            UniqueValidator(queryset=MemberContact.objects.all()),
        ],
    )
    organization_type_of = serializers.IntegerField(required=False,allow_null=True,)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    primary_phone = PhoneNumberField(allow_null=True, required=False)
    secondary_phone = PhoneNumberField(allow_null=True, required=False)

    # ------ MEMBER ADDRESS ------ #

    country = serializers.CharField()
    region = serializers.CharField()
    locality = serializers.CharField()
    street_number = serializers.CharField()
    street_name =serializers.CharField()
    apartment_unit = serializers.CharField()
    street_type = serializers.CharField()
    street_type_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    street_direction = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
    postal_code = serializers.CharField()

    # ------ MEMBER WATCH ------ #

    #TODO: IMPLEMENT FIELDS.

    # ------ MEMBER METRICS ------ #

    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True, required=False,)
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )
    how_hear_other = serializers.CharField(required=False, allow_null=True, allow_blank=True,)
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
    volunteer = serializers.IntegerField()
    another_household_member_registered = serializers.BooleanField()
    year_of_birth = serializers.IntegerField()
    total_household_count = serializers.IntegerField()
    under_18_years_household_count = serializers.IntegerField()
    organization_employee_count = serializers.IntegerField()
    organization_founding_year = serializers.IntegerField()
    organization_type_of = serializers.IntegerField()

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        #TODO: IMPLEMENT FIELDS.


        # type_of_customer = validated_data.get('type_of', UNASSIGNED_CUSTOMER_TYPE_OF_ID)
        #
        # # Format our telephone(s)
        # fax_number = validated_data.get('fax_number', None)
        # if fax_number:
        #     fax_number = phonenumbers.parse(fax_number, "CA")
        # telephone = validated_data.get('telephone', None)
        # if telephone:
        #     telephone = phonenumbers.parse(telephone, "CA")
        # other_telephone = validated_data.get('other_telephone', None)
        # if other_telephone:
        #     other_telephone = phonenumbers.parse(other_telephone, "CA")
        #
        # #-------------------
        # # Create our user.
        # #-------------------
        # # Extract our "email" field.
        # email = validated_data.get('email', None)
        #
        # # If an email exists then
        # owner = None
        # if email:
        #     owner = SharedUser.objects.create(
        #         first_name=validated_data['given_name'],
        #         last_name=validated_data['last_name'],
        #         email=email,
        #         is_active=True,
        #         franchise=self.context['franchise'],
        #         was_email_activated=True
        #     )
        #
        #     # Attach the user to the `Customer` group.
        #     owner.groups.add(CUSTOMER_GROUP_ID)
        #
        #     # Update the password.
        #     password = validated_data.get('password', None)
        #     owner.set_password(password)
        #     owner.save()
        #     logger.info("Created shared user.")
        #
        # #---------------------------------------------------
        # # Create our `Customer` object in our tenant schema.
        # #---------------------------------------------------
        # customer = Customer.objects.create(
        #     owner=owner,
        #     created_by=self.context['created_by'],
        #     last_modified_by=self.context['created_by'],
        #     description=validated_data.get('description', None),
        #     organization_name=validated_data.get('organization_name', None),
        #     organization_type_of=validated_data.get('organization_type_of', None),
        #
        #     # Profile
        #     given_name=validated_data['given_name'],
        #     last_name=validated_data['last_name'],
        #     middle_name=validated_data['middle_name'],
        #     birthdate=validated_data.get('birthdate', None),
        #     join_date=validated_data.get('join_date', None),
        #     gender=validated_data.get('gender', None),
        #
        #     # Misc
        #     is_senior=validated_data.get('is_senior', False),
        #     is_support=validated_data.get('is_support', False),
        #     job_info_read=validated_data.get('job_info_read', False),
        #     how_hear=validated_data.get('how_hear', 1),
        #     how_hear_other=validated_data.get('how_hear_other', "Not answered"),
        #     type_of=type_of_customer,
        #     created_from = self.context['created_from'],
        #     created_from_is_public = self.context['created_from_is_public'],
        #
        #     # Contact Point
        #     email=email,
        #     area_served=validated_data.get('area_served', None),
        #     available_language=validated_data.get('available_language', None),
        #     contact_type=validated_data.get('contact_type', None),
        #     fax_number=fax_number,
        #     # 'hours_available', #TODO: IMPLEMENT.
        #     telephone=telephone,
        #     telephone_extension=validated_data.get('telephone_extension', None),
        #     telephone_type_of=validated_data.get('telephone_type_of', None),
        #     other_telephone=other_telephone,
        #     other_telephone_extension=validated_data.get('other_telephone_extension', None),
        #     other_telephone_type_of=validated_data.get('other_telephone_type_of', None),
        #
        #     # Postal Address
        #     address_country=validated_data.get('address_country', None),
        #     address_locality=validated_data.get('address_locality', None),
        #     address_region=validated_data.get('address_region', None),
        #     post_office_box_number=validated_data.get('post_office_box_number', None),
        #     postal_code=validated_data.get('postal_code', None),
        #     street_address=validated_data.get('street_address', None),
        #     street_address_extra=validated_data.get('street_address_extra', None),
        #
        #     # Geo-coordinate
        #     elevation=validated_data.get('elevation', None),
        #     latitude=validated_data.get('latitude', None),
        #     longitude=validated_data.get('longitude', None),
        #     # 'location' #TODO: IMPLEMENT.
        # )
        # logger.info("Created customer.")
        #
        # #------------------------
        # # Set our `Tag` objects.
        # #------------------------
        # tags = validated_data.get('tags', None)
        # if tags is not None:
        #     if len(tags) > 0:
        #         customer.tags.set(tags)
        #
        # #-----------------------------
        # # Create our `Comment` object.
        # #-----------------------------
        # extra_comment = validated_data.get('extra_comment', None)
        # if extra_comment is not None:
        #     comment = Comment.objects.create(
        #         created_by=self.context['created_by'],
        #         last_modified_by=self.context['created_by'],
        #         text=extra_comment,
        #         created_from = self.context['created_from'],
        #         created_from_is_public = self.context['created_from_is_public']
        #     )
        #     CustomerComment.objects.create(
        #         about=customer,
        #         comment=comment,
        #     )
        #
        # # Update validation data.
        # # validated_data['comments'] = CustomerComment.objects.filter(customer=customer)
        # validated_data['created_by'] = self.context['created_by']
        # validated_data['last_modified_by'] = self.context['created_by']
        # validated_data['extra_comment'] = None
        # validated_data['telephone'] = telephone
        # validated_data['fax_number'] = fax_number
        # validated_data['other_telephone'] = other_telephone
        # validated_data['id'] = customer.id

        # Return our validated data.
        return validated_data
