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
from tenant_associate.permissions import CanRetrieveUpdateDestroyAssociatePermission
from tenant_associate.serializers import AssociateDemoteOperationSerializer, AssociateRetrieveSerializer


class AssociateDemoteOperationAPIView(generics.CreateAPIView):
    serializer_class = AssociateDemoteOperationSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyAssociatePermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        write_serializer = AssociateDemoteOperationSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        write_serializer.is_valid(raise_exception=True)
        associate = write_serializer.save()
        read_serializer = AssociateRetrieveSerializer(associate, many=False,)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
