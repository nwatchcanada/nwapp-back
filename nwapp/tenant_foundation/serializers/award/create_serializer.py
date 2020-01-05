# -*- coding: utf-8 -*-
import logging
import django_rq
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.models import SharedUser
from tenant_foundation.models import Award, Tag


logger = logging.getLogger(__name__)


class AwardCreateSerializer(serializers.Serializer):
    user = serializers.SlugField(
        required=True,
        write_only=True,
    )
    type_of = serializers.ChoiceField(
        required=True,
        allow_null=False,
        choices=Award.TYPE_OF_CHOICES,
        write_only=True,
    )
    type_of_other = serializers.CharField( #TODO: Required if ```type_of == 1```.
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    description_other = serializers.CharField( #TODO: Required if ```type_of == 1```.
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    icon = serializers.CharField( #TODO: Required if ```type_of == 1```.
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    colour = serializers.CharField( #TODO: Required if ```type_of == 1```.
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    # tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True, write_only=True,)

    def validate_user(self, value):
        #TODO: ADD SECURITY SO NON-EXECUTIVES CANNOT ATTACH TO OTHER USERS.
        if not SharedUser.objects.filter(slug=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    # def validate_organization_name(self, value):
    #     """
    #     Custom validation to handle case of user selecting an organization type
    #     of member but then forgetting to fill in the `organization_name` field.
    #     """
    #     request = self.context.get('request')
    #     type_of = request.data.get('type_of')
    #     if type_of == Award.MEMBER_TYPE_OF.BUSINESS:
    #         if value == None or value == "":
    #             raise serializers.ValidationError(_('Please fill this field in.'))
    #     return value

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        slug = validated_data.get('user')
        user = SharedUser.objects.get(slug=slug)
        request = self.context.get("request")
        type_of = validated_data.get('type_of')
        type_of_other = validated_data.get('type_of_other', "")
        description_other = validated_data.get('description_other', "")
        icon = validated_data.get('icon', "")
        colour = validated_data.get('colour', "")

        if type_of == Award.TYPE_OF.SUPPORTER:
            icon = "donate"
            colour = "green"

        award = Award.objects.create(
            user=user,
            type_of=type_of,
            type_of_other=type_of_other,
            description_other=description_other,
            icon=icon,
            colour=colour,
        )

        logger.info("Awarded score points to the user\'s account.")

        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                award.tags.set(tags)
                logger.info("Awarded score has tags attached to it.")

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "error": "Terminating for debugging purposes only."
        # })

        return award
