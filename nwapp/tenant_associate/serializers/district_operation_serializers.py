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
    Associate,
    District
)


logger = logging.getLogger(__name__)


class AssociateDistrictOperationSerializer(serializers.Serializer):
    associate = serializers.SlugField(write_only=True, required=True)
    district = serializers.SlugField(write_only=True, required=True)

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
        associate_slug = validated_data.get('associate')
        associate = Associate.objects.select_for_update().get(user__slug=associate_slug)
        district_slug = validated_data.get('district')
        district = District.objects.get(slug=district_slug)
        request = self.context.get('request')

        # Add our new governing member of district.
        district.governors.add(associate)
        district.last_modified_by=request.user
        district.last_modified_from=request.client_ip
        district.last_modified_from_is_public=request.client_ip_is_routable
        district.save()

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        logger.info("Associate become a governing member of the district.")

        return associate
