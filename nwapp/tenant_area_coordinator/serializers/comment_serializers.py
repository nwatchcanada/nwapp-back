# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Comment,
    AreaCoordinatorComment,
    AreaCoordinator
)

class AreaCoordinatorCommentListSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True,)
    area_coordinator = serializers.SlugField(
        read_only=True,
        source="area_coordinator.user.slug",
    )
    area_coordinator_full_name = serializers.SerializerMethodField()
    text = serializers.CharField(source="comment.text", read_only=True,)
    created_by = serializers.SlugField(
        read_only=True,
        source="comment.created_by.slug",
    )
    created_by_full_name = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = AreaCoordinatorComment
        fields = (
            'slug',
            'created_at',
            'created_by',
            'created_by_full_name',
            'area_coordinator',
            'area_coordinator_full_name',
            'text',
        )

    def get_created_by(self, obj):
        try:
            return str(obj.comment.created_by)
        except Exception as e:
            return None

    def get_area_coordinator_full_name(self, obj):
        try:
            return obj.area_coordinator.get_full_name()
        except Exception as e:
            return None

    def get_created_by_full_name(self, obj):
        try:
            return obj.comment.created_by.get_full_name()
        except Exception as e:
            return None

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'area_coordinator',
            'area_coordinator__user',
            'comment'
        )
        return queryset


class AreaCoordinatorCommentCreateSerializer(serializers.Serializer):
    area_coordinator = serializers.SlugField(write_only=True,)
    text = serializers.CharField(write_only=True,)

    # Meta Information.
    class Meta:
        model = AreaCoordinatorComment
        fields = (
            'area_coordinator',
            'text',
        )

    def validate_area_coordinator(self, value):
        does_exist = AreaCoordinator.objects.filter(user__slug=value).exists()
        if does_exist:
            return value
        else:
            raise serializers.ValidationError(_("AreaCoordinator does not exist."))

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context.get('request')

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        slug = validated_data.get('area_coordinator', None)
        text = validated_data.get('text', None)
        area_coordinator = AreaCoordinator.objects.get(user__slug=slug)

        comment = Comment.objects.create(
            created_by = request.user,
            created_from = request.client_ip,
            created_from_is_public = request.client_ip_is_routable,
            last_modified_by = request.user,
            last_modified_from = request.client_ip,
            last_modified_from_is_public = request.client_ip_is_routable,
            text=text
        )
        area_coordinator_comment = AreaCoordinatorComment.objects.create(
            area_coordinator=area_coordinator,
            comment=comment,
        )

        # raise serializers.ValidationError({ # Uncomment when not using this code but do not delete!
        #     "non_field_error": "Terminating for debugging purposes only."
        # })

        return area_coordinator_comment
