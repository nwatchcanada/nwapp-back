from rest_framework import permissions


class DisableOptionsPermission(permissions.BasePermission):
    """
    Global permission to disallow all requests for method OPTIONS.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return False
        return True


from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions


class SharedUserIsActivePermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint because your account is suspended or not logged in.')

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_active

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.is_active

        return False
