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
from tenant_foundation.serializers import ExpectationItemListCreateSerializer, ExpectationItemRetrieveUpdateDestroySerializer
from tenant_foundation.models import ExpectationItem


class ExpectationItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ExpectationItemListCreateSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanListCreateExpectationItemPermission
    )
    # filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = ExpectationItem.objects.all().order_by('text')

        # # The following code will use the 'django-filter'
        # filter = ExpectationItemFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = ExpectationItemListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
