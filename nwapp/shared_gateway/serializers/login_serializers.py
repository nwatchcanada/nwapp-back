# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from shared_foundation.models import SharedUser


class SharedLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        request = self.context.get('request', None)

        try:
            user = SharedUser.objects.get(email=email)
        except SharedUser.DoesNotExist:
            raise exceptions.ValidationError(_('This E-Mail address is not registered.'))

        authenticated_user = authenticate(request, username=email, password=password)

        if authenticated_user:
            attrs['authenticated_user'] = authenticated_user
            return attrs
        else:
            if not user.was_email_activated:
                raise exceptions.ValidationError(_('Your account was not activated!'))
            if not user.is_active:
                raise exceptions.ValidationError(_('Your account is suspended!'))
            raise exceptions.ValidationError(_('Wrong password or email!'))
