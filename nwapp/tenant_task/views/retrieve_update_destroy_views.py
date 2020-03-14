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
from tenant_task.serializers import TaskItemRetrieveSerializer, TaskItemUpdateSerializer


class TaskItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyTaskItemPermission
    )

    @transaction.atomic
    def get(self, request, uuid=None):
        """
        Retrieve
        """
        order = get_object_or_404(TaskItem, uuid=uuid)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = TaskItemRetrieveSerializer(order, many=False, context={'request': request,})
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
        object = get_object_or_404(TaskItem, uuid=uuid)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = TaskItemUpdateSerializer(
            object,
            data=request.data,
            context={
                'request': request,
                'type_of': object.type_of
            }
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()
        read_serializer = TaskItemRetrieveSerializer(object, many=False, context={'request': request,})
        return Response(read_serializer.data, status=status.HTTP_200_OK)
