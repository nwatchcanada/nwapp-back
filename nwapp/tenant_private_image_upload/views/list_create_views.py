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
from tenant_private_image_upload.filters import PrivateImageUploadFilter
from tenant_private_image_upload.permissions import CanListCreatePrivateImageUploadPermission
from tenant_private_image_upload.serializers import (
    PrivateImageUploadCreateSerializer,
    PrivateImageUploadListSerializer,
    PrivateImageUploadRetrieveSerializer
)
from tenant_foundation.models import PrivateImageUpload


class PrivateImageUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PrivateImageUploadListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreatePrivateImageUploadPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = PrivateImageUpload.objects.all().order_by('created_at')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = PrivateImageUploadFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        post_serializer = PrivateImageUploadCreateSerializer(
            data=request.data,
            context={'request': request,
        });
        post_serializer.is_valid(raise_exception=True)
        member = post_serializer.save()
        retrieve_serializer = PrivateImageUploadRetrieveSerializer(member, many=False)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
