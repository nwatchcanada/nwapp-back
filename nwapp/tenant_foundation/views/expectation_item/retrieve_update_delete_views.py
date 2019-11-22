# -*- coding: utf-8 -*-
from ipware import get_client_ip
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_api.filters.expectation_item import ExpectationItemFilter
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.expectation_item import (
#    CanListCreateExpectationItemPermission,
#    CanRetrieveUpdateDestroyExpectationItemPermission
# )
from tenant_foundation.serializers import ExpectationItemRetrieveUpdateDestroySerializer
from tenant_foundation.models import ExpectationItem


class ExpectationItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpectationItemRetrieveUpdateDestroySerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyExpectationItemPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        expectation_item = get_object_or_404(ExpectationItem, pk=pk)
        self.check_object_permissions(request, expectation_item)  # Validate permissions.
        serializer = ExpectationItemRetrieveUpdateDestroySerializer(expectation_item, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        expectation_item = get_object_or_404(ExpectationItem, pk=pk)
        self.check_object_permissions(request, expectation_item)  # Validate permissions.
        serializer = ExpectationItemRetrieveUpdateDestroySerializer(expectation_item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        expectation_item = get_object_or_404(ExpectationItem, pk=pk)
        self.check_object_permissions(request, expectation_item)  # Validate permissions.
        expectation_item.is_archived = True
        expectation_item.last_modified_by = request.user
        expectation_item.last_modified_from = client_ip
        expectation_item.last_modified_from_is_public = is_routable
        expectation_item.save()
        return Response(data=[], status=status.HTTP_200_OK)
