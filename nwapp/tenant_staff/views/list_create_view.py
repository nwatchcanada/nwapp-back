# -*- coding: utf-8 -*-
import django_rq
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from shared_foundation.models import SharedGroup
from tenant_staff.filters import StaffFilter
from tenant_staff.permissions import CanListCreateStaffPermission
from tenant_staff.serializers import (
    StaffCreateSerializer,
    StaffListSerializer,
    StaffRetrieveSerializer
)
from tenant_foundation.models import Staff
from tenant_staff.tasks import geocode_staff_address_func, geoip2_staff_audit_func


class StaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreateStaffPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Staff.objects.filter(
            Q(user__groups__id=SharedGroup.GROUP_MEMBERSHIP.MANAGER)|
            Q(user__groups__id=SharedGroup.GROUP_MEMBERSHIP.FRONTLINE_STAFF)
        ).order_by('-id')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = StaffFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        post_serializer = StaffCreateSerializer(
            data=request.data,
            context={'request': request,
        });
        post_serializer.is_valid(raise_exception=True)
        staff = post_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_staff_audit_func, request.tenant, staff)
        django_rq.enqueue(geoip2_staff_address_audit_func, request.tenant, staff.address)

        retrieve_serializer = StaffRetrieveSerializer(staff, many=False)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
