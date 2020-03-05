# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_item.filters import ItemCommentFilter
# from tenant_api.pagination import TinyResultsSetPagination
from tenant_item.permissions import (
   CanListCreateItemPermission,
   CanRetrieveUpdateDestroyItemCommentPermission
)
from tenant_item.serializers import (
    ItemCommentListSerializer,
    ItemCommentCreateSerializer
)
from tenant_foundation.models import ItemComment


class ItemCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ItemCommentListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyItemCommentPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = ItemComment.objects.all().order_by(
            '-created_at'
        ).prefetch_related(
            'item',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = ItemCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        write_serializer = ItemCommentCreateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        obj = write_serializer.save()

        read_serializer = ItemCommentListSerializer(
            obj,
            many=False,
            context={
                'request': request
            },
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
