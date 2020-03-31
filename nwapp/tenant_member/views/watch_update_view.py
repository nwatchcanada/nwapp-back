# -*- coding: utf-8 -*-
import django_rq
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import Member
from tenant_member.permissions import CanRetrieveUpdateDestroyMemberPermission
from tenant_member.serializers.retrieve_serializer import MemberRetrieveSerializer
from tenant_member.serializers.watch_update_serializer import MemberWatchUpdateSerializer
from tenant_member.tasks import geoip2_member_audit_func


class MemberWatchUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyMemberPermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(Member, user__slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = MemberWatchUpdateSerializer(
            object,
            data=request.data,
            context={'request': request,}
        )
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_member_audit_func, request.tenant, object)

        read_serializer = MemberRetrieveSerializer(object, many=False, context={'request': request,})
        return Response(read_serializer.data, status=status.HTTP_200_OK)
