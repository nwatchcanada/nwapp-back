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
    token = serializers.SerializerMethodField()
    scope = serializers.SerializerMethodField()

    # # --- Misc Fields ---
    # report_email_frequency = serializers.CharField(required=False,allow_blank=True,)
    # type_of = serializers.CharField(required=False,allow_blank=True,)
    # customer_id = serializers.CharField(read_only=True,)
    # customer_data = serializers.JSONField(read_only=True,)
    # subscription_status = serializers.CharField(read_only=True,)

    # --- User Details ---
    email = serializers.CharField(required=True,allow_blank=False,)
    first_name = serializers.CharField(required=True,allow_blank=False,)
    middle_name = serializers.CharField(required=False,allow_blank=True,)
    last_name = serializers.CharField(required=True,allow_blank=False,)
    # avatar = serializers.CharField(required=False,allow_blank=True,)
    # birthdate = serializers.CharField(required=False,allow_blank=True,)
    # nationality = serializers.CharField(required=False,allow_blank=True,)
    # gender = serializers.CharField(required=False,allow_blank=True,)
    #
    # # --- Billing ---
    # billing_given_name = serializers.CharField(required=True,allow_blank=False,)
    # billing_last_name = serializers.CharField(required=True,allow_blank=False,)
    # billing_country = serializers.CharField(required=True,allow_blank=False,)
    # billing_region = serializers.CharField(required=True,allow_blank=False,)
    # billing_locality = serializers.CharField(required=True,allow_blank=False,)
    # billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    # billing_street_address = serializers.CharField(required=True,allow_blank=False,)
    # billing_street_address_extra = serializers.CharField(required=False,allow_blank=True,)
    # billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    # billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    # billing_email = serializers.CharField(required=True,allow_blank=False,)
    # billing_telephone = serializers.CharField(required=True,allow_blank=False,)
    #
    # # --- Shipping ---
    # is_shipping_different_then_billing = serializers.BooleanField(required=True,)
    # shipping_given_name = serializers.CharField(required=True,allow_blank=False,)
    # shipping_last_name = serializers.CharField(required=True,allow_blank=False,)
    # shipping_country = serializers.CharField(required=True,allow_blank=False,)
    # shipping_region = serializers.CharField(required=True,allow_blank=False,)
    # shipping_locality = serializers.CharField(required=True,allow_blank=False,)
    # shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    # shipping_street_address = serializers.CharField(required=True,allow_blank=False,)
    # shipping_street_address_extra = serializers.CharField(required=False,allow_blank=True,allow_null=True,)
    # shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    # shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,allow_null=True,)
    # shipping_email = serializers.CharField(required=True,allow_blank=False,)
    # shipping_telephone = serializers.CharField(required=True,allow_blank=False,)
    #
    # # --- Misc ---
    # timezone = serializers.CharField(required=False,allow_blank=False,)
    # was_email_activated = serializers.ReadOnlyField()
    # was_onboarded = serializers.ReadOnlyField()
    # onboarding_survey_data = serializers.ReadOnlyField()
    # dashboard_path = serializers.CharField(read_only=True, source="get_dashboard_path",)
    # latest_invoice = InvoiceListCreateSerializer(read_only=True, many=False)
    # referral_link = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        fields = (
            # --- Authentication Credentials ---
            'token',
            'scope',

            # --- User Details ---
            'email',
            'first_name',
            'middle_name',
            'last_name',

            # # --- Misc Fields ---
            # 'report_email_frequency',
            # 'type_of',
            # 'customer_id',
            # 'customer_data',
            # 'subscription_status',
            # 'was_email_activated',
            # 'was_onboarded',
            # 'onboarding_survey_data',
            # 'is_ok_to_email',
            # 'is_ok_to_text',
            # 'location',
            # 'created_at',
            # 'last_modified_at',
            # 'dashboard_path',
            # 'timezone',
            # 'latest_invoice',
            # 'referral_link',
            #
            # # --- Billing ---
            # 'billing_given_name',
            # 'billing_last_name',
            # 'billing_country',
            # 'billing_region',
            # 'billing_locality',
            # 'billing_postal_code',
            # 'billing_street_address',
            # 'billing_street_address_extra',
            # 'billing_postal_code',
            # 'billing_post_office_box_number',
            # 'billing_email',
            # 'billing_telephone',
            #
            # # --- Shipping ---
            # 'is_shipping_different_then_billing',
            # 'shipping_given_name',
            # 'shipping_last_name',
            # 'shipping_country',
            # 'shipping_region',
            # 'shipping_locality',
            # 'shipping_postal_code',
            # 'shipping_street_address',
            # 'shipping_street_address_extra',
            # 'shipping_postal_code',
            # 'shipping_post_office_box_number',
            # 'shipping_email',
            # 'shipping_telephone',
        )

    def get_token(self, obj):
        return self.context.get('token', None)

    def get_scope(self, obj):
        return self.context.get('scope', None)

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
