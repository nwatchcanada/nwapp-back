from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions
# from shared_foundation.utils import has_permission


class CanListTenantPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # Check to see if the user is anonymous or not.
        if request.user.is_anonymous:
            print("CanListTenantPermission | Anonymous users cannot view.")
            return False

        # Check to see if the request is inside a schema or not.
        if request.schema == "www" or request.schema == None:
            print("CanListTenantPermission | Not a tenant schema.")
            return False

        # Administrative permission needs to be evaluated before moving forward.
        if request.user.is_staff or request.user.is_executive:
            return True

        # Check to see if the authenticated user's tenant membership belongs
        # to the request tenant.
        if request.user.tenant == request.tenant:
            return True

        # For debugging purposes
        # print(request.tenant)
        # print(request.user.tenant)

        # Deny permission because the above condition was not met.
        print("CanListTenantPermission | Not a member of tenant.")
        return False


class CanRetrieveUpdateDestroyTenantPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        # print("has_object_permission", request.method)  # For debugging purposes only.

        # # --- RETRIEVE ---
        # if "GET" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_get_associate', request.user, request.user.groups.all())
        #
        # # ---UPDATE ---
        # if "PUT" in request.method:
        #     # OWNERSHIP BASED
        #     if request.user == obj.owner:
        #         return True
        #
        #     # PERMISSION BASED
        #     return has_permission('can_put_associate', request.user, request.user.groups.all())
        #
        # # --- DELETE ---
        # if "DELETE" in request.method:
        #     # PERMISSION BASED
        #     return has_permission('can_delete_associate', request.user, request.user.groups.all())

        return False
