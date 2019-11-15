# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.models import SharedOrganization
from shared_organization.serializers import SharedOrganizationListCreateSerializer


class SharedOrganizationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SharedOrganizationListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        """
        Overriding the initial queryset
        """
        queryset = SharedOrganization.objects.all().exclude(schema_name="public").order_by('name')

        # Set up eager loading to avoid N+1 selects
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = SharedOrganizationListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': request.client_ip,
            'created_from_is_routable': request.client_ip_is_routable,
            'request': request,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # return Response([], status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
