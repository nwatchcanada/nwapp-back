# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_watch.filters import WatchCommentFilter
# from tenant_api.pagination import TinyResultsSetPagination
from tenant_watch.permissions import (
   CanListCreateWatchPermission,
   CanRetrieveUpdateDestroyWatchCommentPermission
)
from tenant_watch.serializers import (
    WatchCommentListSerializer,
    WatchCommentCreateSerializer
)
from tenant_foundation.models import WatchComment


class WatchCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WatchCommentListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyWatchCommentPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = WatchComment.objects.all().order_by(
            '-created_at'
        ).prefetch_related(
            'watch',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = WatchCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        write_serializer = WatchCommentCreateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        obj = write_serializer.save()

        read_serializer = WatchCommentListSerializer(
            obj,
            many=False,
            context={
                'request': request
            },
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
