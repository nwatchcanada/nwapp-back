from rest_framework import permissions
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _


class DisableOptionsPermission(permissions.BasePermission):
    """
    Global permission to disallow all requests for method OPTIONS.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return False
        return True


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


class PublicPermission(permissions.BasePermission):
    """
    Global permission to visiting if from tenant subdomain.
    """
    message = _('You cannot access public API endpoint with a sub-domain your URL.')

    def has_permission(self, request, view):
        return request.tenant.is_public


class TenantPermission(permissions.BasePermission):
    """
    Global permission to verify tenant membership for the authenticated user
    and ensuring proper sub-domain is used. Note: Executive users get automatic
    access if the sub-domain is valid.
    """
    message = _('You cannot access tenant API endpoint without a sub-domain in your URL or without membership in the tenant.')

    def has_permission(self, request, view):
        is_tenant = not request.tenant.is_public
        can_view_tenant = request.user.tenant == request.tenant or request.user.is_executive
        return is_tenant and can_view_tenant
