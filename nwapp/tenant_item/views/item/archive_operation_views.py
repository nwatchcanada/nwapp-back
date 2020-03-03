# -*- coding: utf-8 -*-
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_item.permissions import CanRetrieveUpdateDestroyItemPermission
from tenant_item.serializers import ItemArchiveOperationSerializer, ItemRetrieveSerializer


class ItemArchiveOperationAPIView(generics.CreateAPIView):
    serializer_class = ItemArchiveOperationSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyItemPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        serializer = ItemArchiveOperationSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        serializer = ItemRetrieveSerializer(item, many=False, context={
            'request': request,
        })
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
