# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_api.filters.how_did_you_hear import MeaningItemFilter
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.tag import (
#    CanListCreateTagPermission,
#    CanRetrieveUpdateDestroyTagPermission
# )
from tenant_foundation.serializers import (
    MeaningItemListCreateSerializer,
    MeaningItemRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import MeaningItem


class MeaningItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeaningItemRetrieveUpdateDestroySerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyTagPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        hhi = get_object_or_404(MeaningItem, pk=pk)
        self.check_object_permissions(request, hhi)  # Validate permissions.
        serializer = MeaningItemRetrieveUpdateDestroySerializer(hhi, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        hhi = get_object_or_404(MeaningItem, pk=pk)
        self.check_object_permissions(request, hhi)  # Validate permissions.
        serializer = MeaningItemRetrieveUpdateDestroySerializer(hhi, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        hhi = get_object_or_404(MeaningItem, pk=pk)
        self.check_object_permissions(request, hhi)  # Validate permissions.
        hhi.is_archived = True
        hhi.last_modified_by = request.user
        hhi.last_modified_from = client_ip
        hhi.last_modified_from_is_public = is_routable
        hhi.save()
        return Response(data=[], status=status.HTTP_200_OK)
