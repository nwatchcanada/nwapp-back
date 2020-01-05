# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import AssociateComment
from django.db import models


class AssociateCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('associate', 'associate'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = AssociateComment
        fields = [
            'associate',
            'created_at',
        ]
