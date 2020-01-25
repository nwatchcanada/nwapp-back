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
# from tenant_api.filters.tag import ResourceItemFilter
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.tag import (
#    CanListCreateResourceItemPermission,
#    CanRetrieveUpdateDestroyResourceItemPermission
# )
from tenant_foundation.serializers import ResourceItemRetrieveUpdateDestroySerializer
from tenant_foundation.models import ResourceItem


class ResourceItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceItemRetrieveUpdateDestroySerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyResourceItemPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        tag = get_object_or_404(ResourceItem, slug=slug)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = ResourceItemRetrieveUpdateDestroySerializer(tag, many=False, context={
            'request': request,
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        tag = get_object_or_404(ResourceItem, slug=slug)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = ResourceItemRetrieveUpdateDestroySerializer(tag, data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, slug=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        tag = get_object_or_404(ResourceItem, slug=slug)
        self.check_object_permissions(request, tag)  # Validate permissions.
        tag.is_archived = True
        tag.last_modified_by = request.user
        tag.last_modified_from = client_ip
        tag.last_modified_from_is_public = is_routable
        tag.save()
        return Response(data=[], status=status.HTTP_200_OK)
