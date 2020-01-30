# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import WatchComment
from django.db import models


class WatchCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('watch', 'watch'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def watch_filtering(self, queryset, name, value):
        return queryset.filter(watch__slug=value)
        # return queryset.filter(
        #     Q(contact__last_name__icontains=value) |
        #     Q(contact__last_name__istartswith=value) |
        #     Q(contact__last_name__iendswith=value) |
        #     Q(contact__last_name__exact=value) |
        #     Q(contact__last_name__icontains=value)
        # )

    watch = django_filters.CharFilter(method='watch_filtering')

    class Meta:
        model = WatchComment
        fields = [
            'watch',
            'created_at',
        ]
