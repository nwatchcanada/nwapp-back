# -*- coding: utf-8 -*-
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import (
    SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
)
from shared_foundation.models import SharedGroup
from tenant_task.filters import TaskItemFilter
from tenant_task.permissions import CanListCreateTaskItemPermission
from tenant_task.serializers import (
    # TaskItemCreateSerializer,
    TaskItemListSerializer,
    TaskItemRetrieveSerializer
)
from tenant_foundation.models import TaskItem


class TaskItemListAPIView(generics.ListAPIView):
    serializer_class = TaskItemListSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreateTaskItemPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = TaskItem.objects.all().order_by('-id')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = TaskItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    # @transaction.atomic
    # def post(self, request, format=None):
    #     """
    #     Create
    #     """
    #     post_serializer = TaskItemCreateSerializer(
    #         data=request.data,
    #         context={'request': request,
    #     });
    #     post_serializer.is_valid(raise_exception=True)
    #     task = post_serializer.save()
    #     retrieve_serializer = TaskItemRetrieveSerializer(task, many=False)
    #     return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
