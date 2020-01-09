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


class StaffDemoteOperationSerializer(serializers.Serializer):
    staff = serializers.SlugField(write_only=True, required=True)
    role_id = serializers.IntegerField(write_only=True, required=True,)
    reason = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=Staff.DEMOTION_REASON_CHOICES
    )
    reason_other = serializers.CharField(
        write_only=True,
        required=True,
        allow_null=True,
        allow_blank=True,
    )

    def validate(self, dirty_data):
        """
        Override the validation code to add additional functionionality.
        """
        slug = dirty_data.get('staff')
        staff = Staff.objects.select_for_update().get(user__slug=slug)
        if staff.user.role_id != SharedGroup.GROUP_MEMBERSHIP.MANAGER and staff.user.role_id != SharedGroup.GROUP_MEMBERSHIP.FRONTLINE_STAFF:
            raise serializers.ValidationError(_("You cannot demote because this user is not staff!"))
        return dirty_data


    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('staff')
        staff = Staff.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')
        role_id = int(validated_data.get('role_id'))
        reason = int(validated_data.get('reason'))
        reason_other = validated_data.get('reason_other')

        # For debugging purposes only.
        logger.info(slug, role_id, reason, reason_other)
        print(slug, role_id, reason, reason_other)

        staff.demotion_reason = reason
        staff.demotion_reason_other = reason_other
        staff.last_modified_by = request.user
        staff.last_modified_from = request.client_ip
        staff.last_modified_from_is_public = request.client_ip_is_routable
        staff.save()

        # Set the user's role to be a area coordinator after clearing the
        # previous group memberships.
        staff.user.groups.clear()
        staff.user.groups.add(role_id)

        #---------------------------
        # Attach our comment.
        #---------------------------
        text = _("Demoted staff by %(name)s.") % {
            'name': str(request.user),
        }
        comment = Comment.objects.create(
            created_by=request.user,
            last_modified_by=request.user,
            text=text,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable
        )
        StaffComment.objects.create(
            staff=staff,
            comment=comment,
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Demoted staff")

        return staff
