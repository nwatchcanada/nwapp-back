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

    def member_filtering(self, queryset, name, value):
        return queryset.filter(member__user__slug=value)
        # return queryset.filter(
        #     Q(contact__last_name__icontains=value) |
        #     Q(contact__last_name__istartswith=value) |
        #     Q(contact__last_name__iendswith=value) |
        #     Q(contact__last_name__exact=value) |
        #     Q(contact__last_name__icontains=value)
        # )

    member = django_filters.CharFilter(method='member_filtering')

    class Meta:
        model = MemberComment
        fields = [
            'member',
            'created_at',
        ]
