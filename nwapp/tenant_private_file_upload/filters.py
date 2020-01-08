# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import PrivateFileUpload
from django.db import models
from django.db.models import Q
from django.utils import timezone


class PrivateFileUploadFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('user', 'user'),
            # ('contact__last_name', 'last_name'),
            # # ('telephone', 'telephone'),
            # ('contact__email', 'email'),
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

    def member_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__slug=value)
        )

    member = django_filters.CharFilter(method='member_filtering')

    def area_coordinator_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__slug=value)
        )

    area_coordinator = django_filters.CharFilter(method='area_coordinator_filtering')

    def associate_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__slug=value)
        )

    associate = django_filters.CharFilter(method='associate_filtering')

    def staff_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__slug=value)
        )

    staff = django_filters.CharFilter(method='staff_filtering')

    class Meta:
        model = PrivateFileUpload
        fields = [
            'user',
            'member',
            'area_coordinator',
            'associate',
            'staff',
            'title',
            'description',
            'tags',
            'is_archived'
        ]
