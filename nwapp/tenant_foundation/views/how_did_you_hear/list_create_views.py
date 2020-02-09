# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_api.filters.how_did_you_hear import HowHearAboutUsItemFilter
# from tenant_api.permissions.tag import (
#    CanListCreateTagPermission,
#    CanRetrieveUpdateDestroyTagPermission
# )
from tenant_foundation.serializers import (
    HowHearAboutUsItemListCreateSerializer,
    HowHearAboutUsItemRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import HowHearAboutUsItem


class HowHearAboutUsItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HowHearAboutUsItemListCreateSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanListCreateTagPermission
    )
    # filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = HowHearAboutUsItem.objects.all().order_by('sort_number')

        # # The following code will use the 'django-filter'
        # filter = HowHearAboutUsItemFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = HowHearAboutUsItemListCreateSerializer(data=request.data, context={
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
