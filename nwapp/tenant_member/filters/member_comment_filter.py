# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import MemberComment
from django.db import models


class MemberCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('member', 'member'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = MemberComment
        fields = [
            'member',
            'created_at',
        ]
