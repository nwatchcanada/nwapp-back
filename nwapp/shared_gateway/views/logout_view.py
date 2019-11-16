# -*- coding: utf-8 -*-
import logging
import pytz
from datetime import datetime
from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from django.http import Http404
from django.utils import timezone
from oauthlib.common import generate_token
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.response import Response

from shared_gateway.serializers import SharedLogoutSerializer
from shared_foundation.drf.permissions import DisableOptionsPermission, PublicPermission


class SharedLogoutAPIView(APIView):
    """
    API endpoint used for users to invalidate their valid oAuth 2.0 token.
    """
    authentication_classes= (OAuth2Authentication,)
    throttle_classes = ()
    permission_classes = (
        DisableOptionsPermission,
        PublicPermission,
    )

    def post(self, request):
        authenticated_user = None
        if request.user.is_authenticated:
            authenticated_user = request.user

        # Serializer to get our login details.
        serializer = SharedLogoutSerializer(data=request.data, context={
            'authenticated_by': authenticated_user,
            'authenticated_from': request.client_ip,
            'authenticated_from_is_public': request.client_ip_is_routable
        })

        # Validate the token.
        serializer.is_valid(raise_exception=True)

        # Return our validated token.
        access_token = serializer.validated_data['access_token']

        # Invalidate the token.
        access_token.expires = pytz.utc.localize(datetime(1985, 1, 1, 00, 00))
        access_token.save()

        return Response(data={'detail': 'You are now logged off.'}, status=status.HTTP_200_OK)
