# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import ItemType
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ItemTypeFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
            ('category', 'category'),
            ('text', 'text'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    # def user_filtering(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(user__slug=value)
    #     )
    #
    # user = django_filters.CharFilter(method='user_filtering')

    class Meta:
        model = ItemType
        fields = [
            'is_archived',
            'category',
            'slug'
        ]
