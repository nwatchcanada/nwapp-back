# -*- coding: utf-8 -*-
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.filters.member import MemberFilter
# from tenant_api.permissions.member import (
#    CanListCreateMemberPermission,
#    CanRetrieveUpdateDestroyMemberPermission
# )
from tenant_member.serializers import (
    MemberCreateSerializer,
    MemberListSerializer
)
from tenant_foundation.models import Member
# from tenant_foundation.constants import UNASSIGNED_CUSTOMER_TYPE_OF_ID


class MemberListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MemberListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
    )
    # filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # search_fields = ('@given_name', '@middle_name', '@last_name', '@email', 'telephone',)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Member.objects.all().order_by('last_name')

        # # The following code will use the 'django-filter'
        # filter = MemberFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = MemberCreateSerializer(data=request.data, context={'request': request,});
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
