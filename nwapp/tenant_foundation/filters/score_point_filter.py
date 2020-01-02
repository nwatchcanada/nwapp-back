# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import ScorePoint
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ScorePointFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = ScorePoint
        fields = [
            'user'
        ]
