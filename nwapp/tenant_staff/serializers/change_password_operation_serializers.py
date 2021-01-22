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

from shared_foundation.drf.validators import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.models import SharedUser, SharedGroup
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Staff,
    StaffComment,
    Staff,
    Staff
)


logger = logging.getLogger(__name__)


class StaffChangePasswordOperationSerializer(serializers.Serializer):
    staff = serializers.SlugField(write_only=True, required=True)
    # Add password adding.
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=63,
        style={'input_type': 'password'},
        # validators = [
        #     MatchingDuelFieldsValidator(
        #         another_field='repeat_password',
        #         message=_("Inputted passwords fields do not match.")
        #     ),
        #     EnhancedPasswordStrengthFieldValidator()
        # ]
    )
    repeat_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=63,
        style={'input_type': 'password'}
    )

    def validate_staff(self, value):
        does_exist = Staff.objects.filter(user__slug=value).exists()
        if does_exist:
            return value
        else:
            raise serializers.ValidationError(_("Staff does not exist."))

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('staff')
        staff = Staff.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')
        password = validated_data.get('password')
        repeat_password = validated_data.get('repeat_password')

        logger.info("Beginning changing password...")

        # Update the password if required.
        if password and repeat_password:
            if staff.user:
                staff.user.set_password(password)
                staff.user.save()

        # # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        # #     "error": "Terminating for debugging purposes only."
        # # })

        logger.info("Changed password.")

        return staff
