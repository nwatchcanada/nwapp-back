# -*- coding: utf-8 -*-
import django_rq
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
from tenant_member.filters import MemberFilter
from tenant_member.permissions import CanListCreateMemberPermission
from tenant_member.serializers import (
    MemberCreateSerializer,
    MemberListSerializer,
    MemberRetrieveSerializer
)
from tenant_foundation.models import Member
from tenant_member.tasks import (
    geocode_member_address_func,
    geoip2_member_audit_func,
    geoip2_member_address_audit_func
)


class MemberListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MemberListSerializer
    # pagination_class = TinyResultsSetPagination
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        CanListCreateMemberPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Member.objects.all().order_by('contact__last_name')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = MemberFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        post_serializer = MemberCreateSerializer(
            data=request.data,
            context={'request': request,
        });
        post_serializer.is_valid(raise_exception=True)
        member = post_serializer.save()

        # Run the following functions in the background so our API performance
        # would not be impacted with not-import computations.
        django_rq.enqueue(geoip2_member_audit_func, request.tenant, member)
        django_rq.enqueue(geoip2_member_address_audit_func, request.tenant, member.address)

        retrieve_serializer = MemberRetrieveSerializer(member, many=False)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)
