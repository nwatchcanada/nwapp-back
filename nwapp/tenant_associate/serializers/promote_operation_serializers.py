# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.template.loader import render_to_string  # HTML / TXT
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.constants import *
from shared_foundation.models import SharedUser, SharedGroup
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Associate,
    AssociateComment,
    Associate,
    Associate,
    Staff
)


logger = logging.getLogger(__name__)


class AssociatePromoteOperationSerializer(serializers.Serializer):
    associate = serializers.SlugField(write_only=True, required=True)
    role_id = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=(
            (MANAGEMENT_GROUP_ID, _('Management')),
            (FRONTLINE_GROUP_ID, _('Frontline')),
        )
    )
    conflict_of_interest_agreement = serializers.BooleanField(write_only=True, required=True,)
    code_of_conduct_agreement = serializers.BooleanField(write_only=True, required=True,)
    confidentiality_agreement = serializers.BooleanField(write_only=True, required=True,)
    staff_agreement = serializers.BooleanField(write_only=True, required=True,)
    police_check_date = serializers.DateField(write_only=True, required=True,)

    def validate(self, dirty_data):
        """
        Override the validation code to add additional functionionality.
        """
        slug = dirty_data.get('associate')
        associate = Associate.objects.select_for_update().get(user__slug=slug)
        if associate.user.role_id != SharedGroup.GROUP_MEMBERSHIP.ASSOCIATE:
            raise serializers.ValidationError(_("You cannot promote because this user is not an associate!"))
        return dirty_data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('associate')
        associate = Associate.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')
        role_id = validated_data.get('role_id')
        conflict_of_interest_agreement = validated_data.get('conflict_of_interest_agreement')
        code_of_conduct_agreement = validated_data.get('code_of_conduct_agreement')
        confidentiality_agreement = validated_data.get('confidentiality_agreement')
        staff_agreement = validated_data.get('staff_agreement')
        police_check_date = validated_data.get('police_check_date')

        logger.info("Beginning promotion...")

        # Get the text agreement which will be signed.
        conflict_of_interest_agreement = render_to_string('account/conflict_of_interest_agreement/2019_05_01.txt', {})
        code_of_conduct_agreement = render_to_string('account/code_of_conduct_agreement/2019_05_01.txt', {})
        confidentiality_agreement = render_to_string('account/confidentiality_agreement/2019_05_01.txt', {})
        staff_agreement = render_to_string('account/staff_agreement/2019_05_01.txt', {})

        # Create or update our model.
        staff, created = Staff.objects.update_or_create(
            user=associate.user,
            defaults={
                'user': associate.user,
                'has_signed_conflict_of_interest_agreement': True,
                'conflict_of_interest_agreement': conflict_of_interest_agreement,
                'conflict_of_interest_agreement_signed_on': timezone.now(),
                'has_signed_code_of_conduct_agreement': True,
                'code_of_conduct_agreement': code_of_conduct_agreement,
                'code_of_conduct_agreement_signed_on': timezone.now(),
                'has_signed_confidentiality_agreement': True,
                'confidentiality_agreement': confidentiality_agreement,
                'confidentiality_agreement_signed_on': timezone.now(),
                'has_signed_staff_agreement': True,
                'staff_agreement': staff_agreement,
                'staff_agreement_signed_on': timezone.now(),
                'police_check_date': police_check_date,
            }
        )

        # Set the user's role to be a area coordinator after clearing the
        # previous group memberships.
        staff.user.groups.clear()
        staff.user.groups.add(role_id)

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Promoted to staff")

        return associate
