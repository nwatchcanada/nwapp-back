# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_associate.filters import AssociateCommentFilter
# from tenant_api.pagination import TinyResultsSetPagination
from tenant_associate.permissions import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociateCommentPermission
)
from tenant_associate.serializers import (
    AssociateCommentListSerializer,
    AssociateCommentCreateSerializer
)
from tenant_foundation.models import AssociateComment


class AssociateCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssociateCommentListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyAssociateCommentPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = AssociateComment.objects.all().order_by(
            '-created_at'
        ).prefetch_related(
            'associate',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = AssociateCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        write_serializer = AssociateCommentCreateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        obj = write_serializer.save()

        read_serializer = AssociateCommentListSerializer(
            obj,
            many=False,
            context={
                'request': request
            },
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
