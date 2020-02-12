# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import District
from django.db import models
from django.db.models import Q
from django.utils import timezone


class DistrictFilter(django_filters.FilterSet):
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

    # def user_filtering(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(user__slug=value)
    #     )
    #
    # user = django_filters.CharFilter(method='user_filtering')

    def keyword_filtering(self, queryset, name, value):
        return District.objects.search(value).order_by('name')

    search = django_filters.CharFilter(method='keyword_filtering')

    class Meta:
        model = District
        fields = [
            'is_archived',
            'type_of',
            'slug',
            'search',
        ]
