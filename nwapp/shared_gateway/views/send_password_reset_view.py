# -*- coding: utf-8 -*-
import django_filters
import django_rq
from django.conf.urls import url, include
from django.core.management import call_command
from django_filters import rest_framework as filters
from django.db.models import Q
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.response import Response

from shared_gateway.serializers import SendPasswordResetSerializer
from shared_gateway.tasks import run_send_reset_password_email_func
from shared_foundation import models


class SendPasswordResetAPIView(APIView):
    throttle_classes = ()
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        # Serialize our POST request and return our serializer object,
        serializer = SendPasswordResetSerializer(data=request.data)

        # Apply our validation.
        serializer.is_valid(raise_exception=True)

        # Send password reset email.
        django_rq.enqueue(run_send_reset_password_email_func, email=serializer.validated_data['email'])

        # Return status true that we successfully registered the user.
        return Response(serializer.data, status=status.HTTP_200_OK)
