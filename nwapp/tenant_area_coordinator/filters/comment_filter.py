# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import AreaCoordinatorComment
from django.db import models


class AreaCoordinatorCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('area_coordinator', 'area_coordinator'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = AreaCoordinatorComment
        fields = [
            'area_coordinator',
            'created_at',
        ]
