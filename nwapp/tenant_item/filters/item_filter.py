# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import Item
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ItemFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
            # ('category', 'category'),
            # ('text', 'text'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def category_filtering(self, queryset, name, value):
        if int(value) == 0:
            return queryset
        return queryset.filter(
            Q(type_of__category=value)
        )

    category = django_filters.CharFilter(method='category_filtering')

    class Meta:
        model = Item
        fields = [
            'state',
            'category',
            'slug'
        ]
