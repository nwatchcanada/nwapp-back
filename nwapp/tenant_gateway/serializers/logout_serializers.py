# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from oauth2_provider.models import Application, AbstractApplication, AbstractAccessToken, AccessToken, RefreshToken


class TenantLogoutSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        token = attrs.get('token', None)
        user = self.context.get('authenticated_by', None)

        access_token = AccessToken.objects.filter(
            token=token,
            user=user
        ).first()
        if access_token is None:
            raise exceptions.ValidationError(_('Authentication token is invalid.'))

        # Save and return our access token.
        attrs['access_token'] = access_token
        return attrs
