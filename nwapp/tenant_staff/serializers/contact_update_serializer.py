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
    Member, MemberContact,
    Staff,
    StaffContact,
    StaffAddress,
    StaffMetric,
    Tag, HowHearAboutUsItem,
    ExpectationItem,
    MeaningItem
)
from tenant_member.tasks import process_member_with_slug_func


logger = logging.getLogger(__name__)


class StaffContactUpdateSerializer(serializers.Serializer):
    # ------ MEMBER CONTACT ------ #

    is_ok_to_email = serializers.BooleanField()
    is_ok_to_text = serializers.BooleanField()
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[
            UniqueValidator(queryset=StaffContact.objects.all()),
        ],
    )
    organization_type_of = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=StaffContact.MEMBER_ORGANIZATION_TYPE_OF_CHOICES,
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=SharedUser.objects.all()),
        ],
    )
    primary_phone = E164PhoneNumberField()
    secondary_phone = E164PhoneNumberField(allow_null=True, required=False)

    def validate_organization_name(self, value):
        """
        Custom validation to handle case of user selecting an organization type
        of staff but then forgetting to fill in the `organization_name` field.
        """
        request = self.context.get('request')
        type_of = request.data.get('type_of')
        if type_of == Member.MEMBER_TYPE_OF.BUSINESS:
            if value == None or value == "":
                raise serializers.ValidationError(_('Please fill this field in.'))
        return value

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        request = self.context.get('request')
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.is_ok_to_email = validated_data.get('is_ok_to_email', instance.is_ok_to_email)
        instance.is_ok_to_text = validated_data.get('is_ok_to_text', instance.is_ok_to_text)
        instance.organization_name = validated_data.get('organization_name', instance.organization_name)
        instance.organization_type_of = validated_data.get('organization_type_of', instance.organization_type_of)
        instance.primary_phone = validated_data.get('primary_phone', instance.primary_phone)
        instance.secondary_phone = validated_data.get('secondary_phone', instance.secondary_phone)
        instance.last_modified_by = request.user
        instance.last_modified_from = request.client_ip
        instance.last_modified_from_is_public = request.client_ip_is_routable

        # # DEVELOPERS NOTE:
        # (1) Non-business staffs cannot have the following fields set,
        #     therefore we need to remove the data if the user submits them.
        if instance.member.type_of != Member.MEMBER_TYPE_OF.BUSINESS:
            instance.organization_name = None
            instance.organization_type_of = MemberContact.MEMBER_ORGANIZATION_TYPE_OF.UNSPECIFIED

        instance.save()
        logger.info("Updated staff contact.")

        '''
        Run in the background the code which will `process` the newly created
        staff object.
        '''
        django_rq.enqueue(
            process_member_with_slug_func,
            request.tenant.schema_name,
            instance.member.user.slug
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
