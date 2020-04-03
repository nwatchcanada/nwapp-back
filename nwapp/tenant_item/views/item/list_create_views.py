# -*- coding: utf-8 -*-
import django_rq
import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
# from tenant_api.permissions.item_type import (
#    CanListCreateItemPermission,
#    CanRetrieveUpdateDestroyItemPermission
# )
from tenant_item.filters import ItemFilter
from tenant_item.serializers import (
    ItemListSerializer, EventItemCreateSerializer, EventItemRetrieveSerializer,
    IncidentItemCreateSerializer, IncidentItemRetrieveSerializer,
    ConcernItemCreateSerializer, ConcernItemRetrieveSerializer,
    InformationItemCreateSerializer, InformationItemRetrieveSerializer,
    CommunityNewsItemCreateSerializer, CommunityNewsItemRetrieveSerializer,
    VolunteerItemCreateSerializer, VolunteerItemRetrieveSerializer,
    ResourceItemCreateSerializer, ResourceItemRetrieveSerializer
)
from tenant_foundation.models import Item, ItemType
from tenant_item.tasks import geoip2_item_audit_func


class ItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ItemListSerializer
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
        # CanListCreateItemPermission
    )
    # filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Item.objects.all().order_by('id')

        # Fetch all the queries.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = ItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        type_of = request.data.get("type_of", None)
        serializer = None

        if type_of == ItemType.CATEGORY.EVENT:
            serializer = EventItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = EventItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.INCIDENT:
            serializer = IncidentItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = IncidentItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.CONCERN:
            serializer = ConcernItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = ConcernItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.INFORMATION:
            serializer = InformationItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = InformationItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.COMMUNITY_NEWS:
            serializer = CommunityNewsItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = CommunityNewsItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.VOLUNTEER:
            serializer = VolunteerItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = VolunteerItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif type_of == ItemType.CATEGORY.RESOURCE:
            serializer = ResourceItemCreateSerializer(data=request.data, context={
                'request': request,
                'type_of': request.data.get("type_of", None)
            })
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            serializer = ResourceItemRetrieveSerializer(obj, many=False,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(data={
                'error': "The type of value is unsupported."
            }, status=status.HTTP_400_BAD_REQUEST)

        # # Run the following functions in the background so our API performance #TODO: IMPLEMENT
        # # would not be impacted with not-import computations.
        # django_rq.enqueue(geoip2_item_audit_func, request.tenant, task)
