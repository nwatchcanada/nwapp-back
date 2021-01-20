# -*- coding: utf-8 -*-
import re
from datetime import timedelta
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from shared_foundation.models import SharedUser
from shared_foundation.drf.validators import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'},
        validators = [
            MatchingDuelFieldsValidator(
                another_field='password_repeat',
                message=_("Inputted passwords fields do not match.")
            ),
            EnhancedPasswordStrengthFieldValidator()
        ]
    )
    password_repeat = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'}
    )
    pr_access_code = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255,
        style={'input_type': 'password'}
    )

    def validate(self, clean_data):
        pr_access_code = clean_data['pr_access_code']
        try:
            clean_data['me'] = SharedUser.objects.get(pr_access_code=pr_access_code)
        except SharedUser.DoesNotExist:
            raise serializers.ValidationError(_("Password reset access code does not exist."))
        return clean_data
