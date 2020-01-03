# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import Badge
from django.db import models
from django.db.models import Q
from django.utils import timezone


class BadgeFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
            ('type_of', 'type_of'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = Badge
        fields = [
            'user',
            'is_archived',
            'type_of',
        ]
