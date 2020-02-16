# -*- coding: utf-8 -*-
from ipware import get_client_ip
import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_api.filters.item_type import ItemTypeFilter
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.item_type import (
#    CanListCreateItemTypePermission,
#    CanRetrieveUpdateDestroyItemTypePermission
# )
from tenant_item.serializers import ItemTypeRetrieveUpdateDestroySerializer
from tenant_foundation.models import ItemType


class ItemTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemTypeRetrieveUpdateDestroySerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyItemTypePermission
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        item_type = get_object_or_404(ItemType, pk=pk)
        self.check_object_permissions(request, item_type)  # Validate permissions.
        serializer = ItemTypeRetrieveUpdateDestroySerializer(item_type, many=False, context={
            'request': request,
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        item_type = get_object_or_404(ItemType, pk=pk)
        self.check_object_permissions(request, item_type)  # Validate permissions.
        serializer = ItemTypeRetrieveUpdateDestroySerializer(item_type, data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        item_type = get_object_or_404(ItemType, pk=pk)
        self.check_object_permissions(request, item_type)  # Validate permissions.
        item_type.is_archived = True
        item_type.last_modified_by = request.user
        item_type.last_modified_from = client_ip
        item_type.last_modified_from_is_public = is_routable
        item_type.save()
        return Response(data=[], status=status.HTTP_200_OK)
