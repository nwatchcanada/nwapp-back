# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import TaskItem
from tenant_task.permissions import CanRetrieveUpdateDestroyTaskItemPermission
from tenant_task.serializers import TaskItemRetrieveSerializer


class TaskItemRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyTaskItemPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        order = get_object_or_404(TaskItem, slug=slug)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = TaskItemRetrieveSerializer(order, many=False, context={'request': request,})
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
