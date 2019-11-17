# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.models import SharedOrganization
from shared_organization.serializers import (
    SharedOrganizationRetrieveSerializer,
    SharedOrganizationUpdateSerializer
)


class SharedOrganizationRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    @transaction.atomic
    def get(self, request, schema_name=None):
        """
        Retrieve
        """
        order = get_object_or_404(SharedOrganization, schema_name=schema_name)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = SharedOrganizationRetrieveSerializer(order, many=False)
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, schema_name=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        object = get_object_or_404(SharedOrganization, schema_name=schema_name)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = SharedOrganizationUpdateSerializer(object, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable
        })
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()
        read_serializer = SharedOrganizationRetrieveSerializer(object, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
