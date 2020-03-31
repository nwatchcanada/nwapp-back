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
from tenant_area_coordinator.permissions import CanRetrieveUpdateDestroyAreaCoordinatorPermission
from tenant_area_coordinator.serializers import AreaCoordinatorDemoteOperationSerializer, AreaCoordinatorRetrieveSerializer
from tenant_area_coordinator.tasks import geoip2_area_coordinator_audit_func


class AreaCoordinatorDemoteOperationAPIView(generics.CreateAPIView):
    serializer_class = AreaCoordinatorDemoteOperationSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyAreaCoordinatorPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        write_serializer = AreaCoordinatorDemoteOperationSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        area_coordinator = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_area_coordinator_audit_func, request.tenant, area_coordinator)

        read_serializer = AreaCoordinatorRetrieveSerializer(area_coordinator, many=False,)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
