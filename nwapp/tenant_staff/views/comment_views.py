# -*- coding: utf-8 -*-
import django_rq
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_staff.filters import StaffCommentFilter
# from tenant_api.pagination import TinyResultsSetPagination
from tenant_staff.permissions import (
   CanListCreateStaffPermission,
   CanRetrieveUpdateDestroyStaffCommentPermission
)
from tenant_staff.serializers import (
    StaffCommentListSerializer,
    StaffCommentCreateSerializer
)
from tenant_foundation.models import StaffComment
from tenant_staff.tasks import geoip2_staff_comment_audit_func


class StaffCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffCommentListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyStaffCommentPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = StaffComment.objects.all().order_by(
            '-created_at'
        ).prefetch_related(
            'staff',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = StaffCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        write_serializer = StaffCommentCreateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        obj = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_staff_comment_audit_func, request.tenant, obj)

        read_serializer = StaffCommentListSerializer(
            obj,
            many=False,
            context={
                'request': request
            },
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
