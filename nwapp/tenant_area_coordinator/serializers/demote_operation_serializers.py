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
    AreaCoordinator,
    AreaCoordinatorComment,
    AreaCoordinator
)


logger = logging.getLogger(__name__)


class AreaCoordinatorDemoteOperationSerializer(serializers.Serializer):
    area_coordinator = serializers.SlugField(write_only=True, required=True)
    role_id = serializers.IntegerField(write_only=True, required=True,)
    reason = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=AreaCoordinator.DEMOTION_REASON_CHOICES
    )
    reason_other = serializers.CharField(
        write_only=True,
        required=True,
        allow_null=True,
        allow_blank=True,
    )
    role_id = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=(
            # (SharedGroup.GROUP_MEMBERSHIP., _('Management')),
            # (SharedGroup.GROUP_MEMBERSHIP.FRONTLINE_STAFF, _('Frontline')),
            # (SharedGroup.GROUP_MEMBERSHIP.ASSOCIATE, _('AreaCoordinator')),
            # (SharedGroup.GROUP_MEMBERSHIP.AREA_COORDINATOR, _('Area Coordinator')),
            (SharedGroup.GROUP_MEMBERSHIP.MEMBER, _('Member')),
        )
    )
    conflict_of_interest_agreement = serializers.BooleanField(write_only=True, required=True,)
    code_of_conduct_agreement = serializers.BooleanField(write_only=True, required=True,)
    confidentiality_agreement = serializers.BooleanField(write_only=True, required=True,)
    police_check_date = serializers.DateField(write_only=True, required=True,)

    def validate(self, dirty_data):
        """
        Override the validation code to add additional functionionality.
        """
        slug = dirty_data.get('area_coordinator')
        area_coordinator = AreaCoordinator.objects.select_for_update().get(user__slug=slug)
        if area_coordinator.user.role_id != SharedGroup.GROUP_MEMBERSHIP.AREA_COORDINATOR and area_coordinator.user.role_id != SharedGroup.GROUP_MEMBERSHIP.FRONTLINE_STAFF:
            raise serializers.ValidationError(_("You cannot demote because this user is not area coordinator!"))
        return dirty_data


    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('area_coordinator')
        area_coordinator = AreaCoordinator.objects.select_for_update().get(user__slug=slug)
        request = self.context.get('request')
        role_id = int(validated_data.get('role_id'))
        reason = int(validated_data.get('reason'))
        reason_other = validated_data.get('reason_other')
        conflict_of_interest_agreement = validated_data.get('conflict_of_interest_agreement')
        code_of_conduct_agreement = validated_data.get('code_of_conduct_agreement')
        confidentiality_agreement = validated_data.get('confidentiality_agreement')
        police_check_date = validated_data.get('police_check_date')

        #---------------------------
        # Reason for demotion.
        #---------------------------

        # Update demotion reason.
        area_coordinator.demotion_reason = reason
        area_coordinator.demotion_reason_other = reason_other
        area_coordinator.last_modified_by = request.user
        area_coordinator.last_modified_from = request.client_ip
        area_coordinator.last_modified_from_is_public = request.client_ip_is_routable
        area_coordinator.save()

        #---------------------------
        # Adjust group membership.
        #---------------------------

        # Set the user's role to be a area coordinator after clearing the
        # previous group memberships.
        area_coordinator.user.groups.clear()
        area_coordinator.user.groups.add(role_id)

        #---------------------------
        # Attach our comment.
        #---------------------------
        text = _("Demoted area coordinator by %(name)s.") % {
            'name': str(request.user),
        }
        comment = Comment.objects.create(
            created_by=request.user,
            last_modified_by=request.user,
            text=text,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable
        )
        AreaCoordinatorComment.objects.create(
            area_coordinator=area_coordinator,
            comment=comment,
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Demoted area coordinator")

        return area_coordinator
