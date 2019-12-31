# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


logger = logging.getLogger(__name__)


class SharedProfileInfoRetrieveUpdateSerializer(serializers.Serializer):
    # --- Authentication Credentials ---
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    schema_name = serializers.SerializerMethodField()
    role_id = serializers.SerializerMethodField()

    # --- User Details ---
    slug = serializers.SlugField(read_only=True,)
    email = serializers.CharField(required=True,allow_blank=False,)
    first_name = serializers.CharField(required=True,allow_blank=False,)
    middle_name = serializers.CharField(required=False,allow_blank=True,)
    last_name = serializers.CharField(required=True,allow_blank=False,)
    # avatar = serializers.CharField(required=False,allow_blank=True,)
    # birthdate = serializers.CharField(required=False,allow_blank=True,)
    # nationality = serializers.CharField(required=False,allow_blank=True,)
    # gender = serializers.CharField(required=False,allow_blank=True,)


    # Meta Information.
    class Meta:
        fields = (
            # --- Authentication Credentials ---
            'access_token',
            'refresh_token',
            'schema_name',
            'role_id',

            # --- User Details ---
            'slug',
            'email',
            'first_name',
            'middle_name',
            'last_name',
        )

    def get_schema_name(self, obj):
        return obj.tenant.schema_name

    def get_role_id(self, obj):
        group = obj.groups.first()
        group_id = None
        if group:
            group_id = group.id
        return group_id

    def get_access_token(self, obj):
        access_token = self.context.get('access_token', None)
        if access_token:
            return {
                'token': str(access_token),
                'expires': int(access_token.expires.timestamp()),
                'scope': str(access_token.scope)
            }
        return None

    def get_refresh_token(self, obj):
        refresh_token = self.context.get('refresh_token', None)
        if refresh_token:
            revoked_at = int(refresh_token.revoked.timestamp()) if refresh_token.revoked is not None else None
            return {
                'token': str(refresh_token),
                'revoked': revoked_at,
            }
        return None

    # def get_referral_link(self, obj):
    #     return settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL + settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN + "/register/"+str(obj.referral_code)
    #
    # def update(self, instance, validated_data):
    #     """
    #     Override this function to include extra functionality.
    #     """
    #     # --- Billing ---
    #     instance.billing_given_name = validated_data.get('billing_given_name', instance.billing_given_name)
    #     instance.billing_last_name = validated_data.get('billing_last_name', instance.billing_last_name)
    #     instance.billing_country = validated_data.get('billing_country', instance.billing_country)
    #     instance.billing_region = validated_data.get('billing_region', instance.billing_region)
    #     instance.billing_locality = validated_data.get('billing_locality', instance.billing_locality)
    #     instance.billing_postal_code = validated_data.get('billing_postal_code', instance.billing_postal_code)
    #     instance.billing_street_address = validated_data.get('billing_street_address', instance.billing_street_address)
    #     instance.billing_street_address_extra = validated_data.get('billing_street_address_extra', instance.billing_street_address_extra)
    #     instance.billing_postal_code = validated_data.get('billing_postal_code', instance.billing_postal_code)
    #     instance.billing_post_office_box_number = validated_data.get('billing_post_office_box_number', instance.billing_post_office_box_number)
    #     instance.billing_email = validated_data.get('billing_email', instance.billing_email)
    #     instance.billing_telephone = validated_data.get('billing_telephone', instance.billing_telephone)
    #
    #     # --- Shipping ---
    #     instance.is_shipping_different_then_billing = validated_data.get('is_shipping_different_then_billing', instance.is_shipping_different_then_billing)
    #     instance.shipping_given_name = validated_data.get('shipping_given_name', instance.shipping_given_name)
    #     instance.shipping_last_name = validated_data.get('shipping_last_name', instance.shipping_last_name)
    #     instance.shipping_country = validated_data.get('shipping_country', instance.shipping_country)
    #     instance.shipping_region = validated_data.get('shipping_region', instance.shipping_region)
    #     instance.shipping_locality = validated_data.get('shipping_locality', instance.shipping_locality)
    #     instance.shipping_postal_code = validated_data.get('shipping_postal_code', instance.shipping_postal_code)
    #     instance.shipping_street_address = validated_data.get('shipping_street_address', instance.shipping_street_address)
    #     instance.shipping_street_address_extra = validated_data.get('shipping_street_address_extra', instance.shipping_street_address_extra)
    #     instance.shipping_postal_code = validated_data.get('shipping_postal_code', instance.shipping_postal_code)
    #     instance.shipping_post_office_box_number = validated_data.get('shipping_post_office_box_number', instance.shipping_post_office_box_number)
    #     instance.shipping_email = validated_data.get('shipping_email', instance.shipping_email)
    #     instance.shipping_telephone = validated_data.get('shipping_telephone', instance.shipping_telephone)
    #
    #     # --- Model ---
    #     instance.save()
    #     return validated_data
