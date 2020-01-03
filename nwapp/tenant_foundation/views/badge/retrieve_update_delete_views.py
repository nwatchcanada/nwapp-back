# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import Badge
# from tenant_member.permissions import CanRetrieveUpdateDestroyBadgePermission
from tenant_foundation.serializers import BadgeRetrieveSerializer


class BadgeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyBadgePermission
    )

    @transaction.atomic
    def get(self, request, uuid=None):
        """
        Retrieve
        """
        sp = get_object_or_404(Badge, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.
        serializer = BadgeRetrieveSerializer(sp, many=False, context={'request': request,})
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, uuid=None):
        """
        Update
        """
        sp = get_object_or_404(Badge, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.
        return Response(data={
            'error': 'Programmer has this as a TODO item'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    @transaction.atomic
    def delete(self, request, uuid=None):
        """
        Delete
        """
        sp = get_object_or_404(Badge, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.

        sp = Badge.archive(
            uuid,
            request.user,
            request.client_ip,
            request.client_ip_is_routable
        )

        serializer = BadgeRetrieveSerializer(sp, many=False, context={'request': request,})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
