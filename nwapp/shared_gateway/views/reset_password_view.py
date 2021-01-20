# -*- coding: utf-8 -*-
import django_filters
import django_rq
from ipware import get_client_ip
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.management import call_command
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from oauthlib.common import generate_token
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status, parsers, renderers
from rest_framework.response import Response

from shared_gateway.serializers import (
# ProfileInfoRetrieveUpdateSerializer,
    ResetPasswordSerializer
)
from shared_foundation.models import SharedUser


class ResetPasswordAPIView(APIView):
    throttle_classes = ()
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request, format=None):
        client_ip, is_routable = get_client_ip(self.request)
        serializer = ResetPasswordSerializer(data=request.data)

        # Perform validation.
        serializer.is_valid(raise_exception=True)

        # Get our validated variables.
        password = serializer.validated_data['password']
        user = serializer.validated_data['me']

        # Update the password.
        user.set_password(password)
        user.save()

        # Security: Remove the "pr_access_code" so it cannot be used again. #TODO: REMOVE.
        user.pr_access_code = ''
        user.save()

        # DEVELOPER NOTES:
        # - The code below is similar to the "sign-in" API endpoint.
        # - We are essentially authenticating the user and creating a
        #   session for the authenticated user.
        # - We will get our API token and return it.
        # - We will return our profile info.

        # Authenticate the user based on the ID and start a session for the user.
        authenticate(request, user_id=user.id)
        login(request, user, backend='foundation.backends.NWAppPasswordlessAuthenticationBackend',)

        # Get our web application authorization.
        application = Application.objects.filter(name=settings.NWAPP_RESOURCE_SERVER_NAME).first()

        # Delete previous access tokens.
        access_tokens = AccessToken.objects.filter(user=user)
        for at in access_tokens.all():
            at.delete()

        # Generate our access token which does not have a time limit.
        aware_dt = timezone.now()
        expires_dt = aware_dt.replace(aware_dt.year + 1776)
        access_token, created = AccessToken.objects.update_or_create(
            application=application,
            user=user,
            defaults={
                'user': user,
                'application': application,
                'expires': expires_dt,
                'token': generate_token(),
                'scope': 'read,write,introspection'
            },
            scope='read,write,introspection'
        )

        # serializer = ProfileInfoRetrieveUpdateSerializer(request.user, many=False, context={
        #     'authenticated_by': request.user,
        #     'authenticated_from': client_ip,
        #     'authenticated_from_is_public': is_routable,
        #     'token': str(access_token),
        #     'scope': 'read,write,introspection'
        # })
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)
