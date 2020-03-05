# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import ItemComment
from django.db import models


class ItemCommentFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('comment__text', 'text'),
            ('item', 'item'),
            ('created_at', 'created_at'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def item_filtering(self, queryset, name, value):
        return queryset.filter(item__slug=value)
        # return queryset.filter(
        #     Q(contact__last_name__icontains=value) |
        #     Q(contact__last_name__istartswith=value) |
        #     Q(contact__last_name__iendswith=value) |
        #     Q(contact__last_name__exact=value) |
        #     Q(contact__last_name__icontains=value)
        # )

    item = django_filters.CharFilter(method='item_filtering')

    class Meta:
        model = ItemComment
        fields = [
            'item',
            'created_at',
        ]
