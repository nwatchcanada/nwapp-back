# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import MemberAddress
from tenant_member.permissions import CanRetrieveUpdateDestroyMemberAddressPermission
from tenant_member.serializers import MemberRetrieveSerializer, MemberAddressUpdateSerializer


class MemberAddressUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyMemberAddressPermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(MemberAddress, member__user__slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = MemberAddressUpdateSerializer(
            object,
            data=request.data,
            context={
                'request': request,
            }
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()

        import django_rq
        from tenant_member.tasks import geocode_member_address_func
        django_rq.enqueue(geocode_member_address_func, request.tenant.schema_name, slug)

        read_serializer = MemberRetrieveSerializer(
            object.member,
            many=False,
            context={
                'request': request,
            }
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)
