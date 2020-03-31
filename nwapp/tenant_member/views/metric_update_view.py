# -*- coding: utf-8 -*-
import django_rq
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_foundation.models import MemberMetric
from tenant_member.permissions import CanRetrieveUpdateDestroyMemberMetricPermission
from tenant_member.serializers import MemberRetrieveSerializer, MemberMetricsUpdateSerializer
from tenant_member.tasks import geoip2_member_metric_audit_func


class MemberMetricUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanRetrieveUpdateDestroyMemberMetricPermission
    )

    @transaction.atomic
    def put(self, request, slug=None):
        """
        Update
        """
        object = get_object_or_404(MemberMetric, member__user__slug=slug)
        self.check_object_permissions(request, object)  # Validate permissions.
        write_serializer = MemberMetricsUpdateSerializer(object, data=request.data, context={'request': request,})
        write_serializer.is_valid(raise_exception=True)
        object = write_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_member_metric_audit_func, request.tenant, object)

        read_serializer = MemberRetrieveSerializer(object.member, many=False, context={'request': request,})
        return Response(read_serializer.data, status=status.HTTP_200_OK)
