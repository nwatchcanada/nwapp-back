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
    TaskItem, AreaCoordinator, Associate
)


logger = logging.getLogger(__name__)


class TaskItemUpdateSerializer(serializers.Serializer):
    area_coordinator_slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True,)
    associate_slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True,)

    def validate_area_coordinator_slug(self, value):
        type_of = self.context.get("type_of")
        if type_of == TaskItem.TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH:
            if value == None or value == "":
                raise serializers.ValidationError(_("Please specify the area coordinator."))
        return value

    def validate_associate_slug(self, value):
        type_of = self.context.get("type_of")
        if type_of == TaskItem.TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH:
            if value == None or value == "":
                raise serializers.ValidationError(_("Please specify the associate."))
        return value

    def update(self, instance, validated_data):
        """
        Override the `update` function to add extra functinality.
        """
        request = self.context.get("request")
        type_of = self.context.get("type_of")
        
        if type_of == TaskItem.TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH:
            slug = validated_data.get("area_coordinator_slug")
            area_coordinator = AreaCoordinator.objects.get(user__slug=slug)
            area_coordinator.user.member.watch = instance.watch
            area_coordinator.user.member.last_modified_by = request.user
            area_coordinator.user.member.last_modified_from = request.client_ip
            area_coordinator.user.member.last_modified_from_is_public = request.client_ip_is_routable
            area_coordinator.user.member.save()
            logger.info("Assigned area coordinator to watch.")

            instance.state = TaskItem.STATE.CLOSED
            instance.last_modified_by = request.user
            instance.last_modified_from = request.client_ip
            instance.last_modified_from_is_public = request.client_ip_is_routable
            instance.save()
            logger.info("Closing task for assigning area coordinator to watch..")

        elif type_of == TaskItem.TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH:
            slug = validated_data.get("associate_slug")
            associate = Associate.objects.get(user__slug=slug)
            associate.user.member.watch = instance.watch
            associate.user.member.last_modified_by = request.user
            associate.user.member.last_modified_from = request.client_ip
            associate.user.member.last_modified_from_is_public = request.client_ip_is_routable
            associate.user.member.save()
            logger.info("Assigned associate to watch.")

            instance.state = TaskItem.STATE.CLOSED
            instance.last_modified_by = request.user
            instance.last_modified_from = request.client_ip
            instance.last_modified_from_is_public = request.client_ip_is_routable
            instance.save()
            logger.info("Closing task for assigning associate to watch.")

        else:
            raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
                "developerError": "Programmer did not implement yet."
            })

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return instance
