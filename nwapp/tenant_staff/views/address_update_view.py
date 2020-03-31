# -*- coding: utf-8 -*-
import django_rq
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import StaffAddress
from tenant_staff.permissions import CanRetrieveUpdateDestroyStaffNodePermission
from tenant_staff.serializers import StaffRetrieveSerializer, StaffAddressUpdateSerializer
from tenant_staff.tasks import geocode_staff_address_func, geoip2_staff_address_audit_func


class StaffAddressUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyStaffNodePermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(StaffAddress, member__user__slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = StaffAddressUpdateSerializer(
            object,
            data=request.data,
            context={
                'request': request,
            }
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geocode_staff_address_func, request.tenant.schema_name, slug)
        django_rq.enqueue(geoip2_staff_address_audit_func, request.tenant, object)

        read_serializer = StaffRetrieveSerializer(
            object.member,
            many=False,
            context={
                'request': request,
            }
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)
