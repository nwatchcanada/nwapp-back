# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import Award
# from tenant_member.permissions import CanRetrieveUpdateDestroyAwardPermission
from tenant_foundation.serializers import AwardRetrieveSerializer


class AwardRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanRetrieveUpdateDestroyAwardPermission
    )

    @transaction.atomic
    def get(self, request, uuid=None):
        """
        Retrieve
        """
        sp = get_object_or_404(Award, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.
        serializer = AwardRetrieveSerializer(sp, many=False, context={'request': request,})
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
        sp = get_object_or_404(Award, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.
        return Response(data={
            'error': 'Programmer has this as a TODO item'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    @transaction.atomic
    def delete(self, request, uuid=None):
        """
        Delete
        """
        sp = get_object_or_404(Award, uuid=uuid)
        self.check_object_permissions(request, sp)  # Validate permissions.

        sp.is_archived = True
        sp.last_modified_by = request.user
        sp.last_modified_from = request.client_ip
        sp.last_modified_from_is_public = request.client_ip_is_routable
        sp.save()

        serializer = AwardRetrieveSerializer(sp, many=False, context={'request': request,})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
