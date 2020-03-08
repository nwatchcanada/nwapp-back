# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import TaskItemComment
from django.db import models


class TaskItemCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('staff', 'staff'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = TaskItemComment
        fields = [
            'staff',
            'created_at',
        ]
