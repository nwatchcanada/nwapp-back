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
from shared_foundation.drf.pagination import StandardResultsSetPagination
# from tenant_api.permissions.tag import (
#    CanListCreateResourceItemPermission,
#    CanRetrieveUpdateDestroyResourceItemPermission
# )
from tenant_foundation.filters import ResourceItemFilter
from tenant_foundation.serializers import (
    ResourceItemListSerializer,
    ResourceItemCreateSerializer,
    ResourceItemRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import ResourceItem


class ResourceItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ResourceItemListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanListCreateResourceItemPermission
    )
    # filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = ResourceItem.objects.all().order_by('name')

        # The following code will use the 'django-filter'
        filter = ResourceItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = ResourceItemCreateSerializer(data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        object = serializer.save()
        serializer = ResourceItemRetrieveUpdateDestroySerializer(object, many=False, context={
            'request': request,
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)
