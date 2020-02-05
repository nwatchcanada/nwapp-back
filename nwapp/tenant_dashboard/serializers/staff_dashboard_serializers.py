# -*- coding: utf-8 -*-
import logging
import django_rq
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers

from shared_foundation.models import SharedOrganization

from tenant_foundation.models import (
    Member, AreaCoordinator, Associate, Watch, Announcement
)
from tenant_foundation.serializers.announcement.list_create_serializers import AnnouncementListCreateSerializer


logger = logging.getLogger(__name__)


class StaffDashboardSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        active_members_count = Member.objects.filter(state=Member.MEMBER_STATE.ACTIVE).count()
        active_watches_count = Watch.objects.filter(is_archived=False).count()
        active_associates_count = Associate.objects.filter(user__member__state=Member.MEMBER_STATE.ACTIVE).count()
        active_announcements = Announcement.objects.filter(is_archived=False)
        announcement_serializer = AnnouncementListCreateSerializer(
            active_announcements,
            many=True,
            context={
                'context': self.context,
            }
        )
        active_tasks_count = 0 #TODO: IMPLEMENT
        return {
            'active_members_count': active_members_count,
            'active_watches_count': active_watches_count,
            'active_associates_count': active_associates_count,
            'active_tasks_count': active_tasks_count,
            'announcements': announcement_serializer.data,
            'latest_tasks': [], #TODO: IMPLEMENT
        }
