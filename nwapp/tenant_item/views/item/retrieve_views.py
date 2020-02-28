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
# from tenant_api.filters.item_type import ItemFilter
# from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.item_type import (
#    CanListCreateItemPermission,
#    CanRetrieveItemPermission
# )
from tenant_item.serializers import ItemRetrieveSerializer
from tenant_foundation.models import Item


class ItemRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ItemRetrieveSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveItemPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        item_type = get_object_or_404(Item, slug=slug)
        self.check_object_permissions(request, item_type)  # Validate permissions.
        serializer = ItemRetrieveSerializer(item_type, many=False, context={
            'request': request,
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
