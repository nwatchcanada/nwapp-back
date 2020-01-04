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
from shared_foundation.models import SharedGroup
from tenant_area_coordinator.filters import AreaCoordinatorFilter
from tenant_area_coordinator.permissions import CanListCreateAreaCoordinatorPermission
from tenant_area_coordinator.serializers import (
    AreaCoordinatorCreateSerializer,
    AreaCoordinatorListSerializer,
    AreaCoordinatorRetrieveSerializer
)
from tenant_foundation.models import AreaCoordinator


class AreaCoordinatorListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AreaCoordinatorListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreateAreaCoordinatorPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = AreaCoordinator.objects.filter(
            user__groups__id=SharedGroup.GROUP_MEMBERSHIP.AREA_COORDINATOR
        ).order_by('-id')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = AreaCoordinatorFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        post_serializer = AreaCoordinatorCreateSerializer(
            data=request.data,
            context={'request': request,
        });
        post_serializer.is_valid(raise_exception=True)
        area_coordinator = post_serializer.save()
        retrieve_serializer = AreaCoordinatorRetrieveSerializer(area_coordinator, many=False)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
