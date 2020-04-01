# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import District
# from tenant_member.permissions import CanRetrieveUpdateDestroyDistrictPermission
from tenant_foundation.serializers import DistrictRetrieveSerializer
from tenant_foundation.serializers import DistrictBoundaryOperationSerializer


class DistrictBoundaryOperationAPIView(generics.UpdateAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyDistrictPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        sp = get_object_or_404(District, slug=slug)
        self.check_object_permissions(request, sp)  # Validate permissions.
        serializer = DistrictRetrieveSerializer(sp, many=False, context={'request': request,})
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(District, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = DistrictBoundaryOperationSerializer(
            object,
            data=request.data,
            context={'request': request,}
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()
        read_serializer = DistrictRetrieveSerializer(
            object,
            many=False,
            context={'request': request,}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    # @transaction.atomic
    # def delete(self, request, slug=None):
    #     """
    #     Delete
    #     """
    #     district = get_object_or_404(District, slug=slug)
    #     self.check_object_permissions(request, district)  # Validate permissions.
    #
    #     district.is_archived = not district.is_archived
    #     district.last_modified_by = request.user
    #     district.last_modified_from = request.client_ip
    #     district.last_modified_from_is_public = request.client_ip_is_routable
    #     district.save()
    #
    #     serializer = DistrictRetrieveSerializer(district, many=False, context={'request': request,})
    #     return Response(data=serializer.data, status=status.HTTP_200_OK)
