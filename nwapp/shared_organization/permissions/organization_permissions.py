from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions


class SharedOrganizationPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        if request.method == "GET":
            if request.user.is_executive:
                return True

        if request.method == "POST":
            if request.user.is_executive:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        return True
        # if request.user.is_authenticated:
        #     return request.user.is_active

        return False
