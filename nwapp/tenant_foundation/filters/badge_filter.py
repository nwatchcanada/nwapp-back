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
            ('user', 'user'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def user_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__slug=value)
        )

    user = django_filters.CharFilter(method='user_filtering')

    class Meta:
        model = Badge
        fields = [
            'user',
            'is_archived',
            'type_of',
        ]
