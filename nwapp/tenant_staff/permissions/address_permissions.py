from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions


class CanListCreateStaffAddressPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # print("has_permission", request.method)  # For debugging purposes only.

        # --- LIST ---
        if "GET" in request.method:
            # PERMISSION BASED
            return request.user.is_executive or request.user.is_management or request.user.is_frontline

        # --- CREATE ---
        if "POST" in request.method:
            # PERMISSION BASED
            return request.user.is_executive or request.user.is_management or request.user.is_frontline

        return False


class CanRetrieveUpdateDestroyStaffAddressPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        # print("has_object_permission", request.method)  # For debugging purposes only.

        # --- RETRIEVE ---
        if "GET" in request.method:
            # OWNERSHIP BASED
            if request.user == obj.staff.user:
                return True

            # PERMISSION BASED
            return request.user.is_executive or request.user.is_management or request.user.is_frontline

        # ---UPDATE ---
        if "PUT" in request.method:
            # OWNERSHIP BASED
            if request.user == obj.staff.user:
                return True

            # PERMISSION BASED
            return request.user.is_executive or request.user.is_management or request.user.is_frontline

        # --- DELETE ---
        if "DELETE" in request.method:
            # PERMISSION BASED
            return request.user.is_executive or request.user.is_management or request.user.is_frontline

        return False
