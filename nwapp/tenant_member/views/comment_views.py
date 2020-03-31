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
from tenant_member.filters import MemberCommentFilter
# from tenant_api.pagination import TinyResultsSetPagination
from tenant_member.permissions import (
   CanListCreateMemberPermission,
   CanRetrieveUpdateDestroyMemberCommentPermission
)
from tenant_member.serializers import (
    MemberCommentListSerializer,
    MemberCommentCreateSerializer
)
from tenant_foundation.models import MemberComment
from tenant_member.tasks import geoip2_member_comment_audit_func


class MemberCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MemberCommentListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyMemberCommentPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = MemberComment.objects.all().order_by(
            '-created_at'
        ).prefetch_related(
            'member',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = MemberCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        write_serializer = MemberCommentCreateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_member_comment_audit_func, request.tenant, object)

        read_serializer = MemberCommentListSerializer(
            object,
            many=False,
            context={
                'request': request
            },
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
