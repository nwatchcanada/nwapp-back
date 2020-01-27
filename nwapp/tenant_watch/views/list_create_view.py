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
from tenant_watch.filters import WatchFilter
from tenant_watch.permissions import CanListCreateWatchPermission
from tenant_watch.serializers import (
    WatchCreateSerializer,
    WatchListSerializer,
    WatchRetrieveSerializer
)
from tenant_foundation.models import Watch


class WatchListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WatchListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreateWatchPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Watch.objects.all().order_by('-id')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = WatchFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        post_serializer = WatchCreateSerializer(
            data=request.data,
            context={'request': request,
        });
        post_serializer.is_valid(raise_exception=True)
        watch = post_serializer.save()
        retrieve_serializer = WatchRetrieveSerializer(watch, many=False)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
