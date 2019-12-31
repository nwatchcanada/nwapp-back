# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import PrivateImageUpload
from tenant_private_image_upload.permissions import CanRetrieveUpdateDestroyPrivateImageUploadPermission
from tenant_private_image_upload.serializers import (
    PrivateImageUploadRetrieveSerializer,
    PrivateImageUploadUpdateSerializer
)


class PrivateImageUploadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyPrivateImageUploadPermission
    )

    @transaction.atomic
    def get(self, request, slug=None):
        """
        Retrieve
        """
        object = get_object_or_404(PrivateImageUpload, user__slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        serializer = PrivateImageUploadRetrieveSerializer(object, many=False, context={'request': request,})
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        object = get_object_or_404(PrivateImageUpload, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = PrivateImageUploadUpdateSerializer(object, data=request.data, context={'request': request,})
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()
        read_serializer = PrivateImageUploadRetrieveSerializer(object, many=False, context={'request': request,})
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, slug=None):
        """
        Delete
        """
        object = get_object_or_404(PrivateImageUpload, slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.

        object.is_archived = not object.is_archived
        object.last_modified_by = request.user
        object.last_modified_from = request.client_ip
        object.last_modified_from_is_public = request.client_ip_is_routable
        object.save()

        serializer = PrivateImageUploadRetrieveSerializer(object, many=False, context={'request': request,})
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
