# -*- coding: utf-8 -*-
import logging
import django_rq
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_foundation.models import SharedOrganization


logger = logging.getLogger(__name__)


class DashboardSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'message': 'test',
        }
