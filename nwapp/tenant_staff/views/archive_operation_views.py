# -*- coding: utf-8 -*-
import django_rq
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_staff.permissions import CanRetrieveUpdateDestroyStaffPermission
from tenant_staff.serializers import StaffArchiveOperationSerializer, StaffRetrieveSerializer
from tenant_staff.tasks import geoip2_staff_audit_func


class StaffArchiveOperationAPIView(generics.CreateAPIView):
    serializer_class = StaffArchiveOperationSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyStaffPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        serializer = StaffArchiveOperationSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_staff_audit_func, request.tenant, staff)

        read_serializer = StaffRetrieveSerializer(staff, many=False,)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
