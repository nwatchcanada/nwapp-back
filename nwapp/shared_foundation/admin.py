from ipware import get_client_ip
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from shared_foundation.models import *


# Define a new SharedUser admin
class SharedUserAdmin(BaseUserAdmin):
    raw_id_fields = ['tenant', 'referred_by',]
    list_display = ['email', 'is_staff', 'is_active', 'was_email_activated',  'tenant',]
    list_filter = ('is_staff',  'is_active', 'was_email_activated', )

    fieldsets = (
        (None,
            {'fields': ('email','password')}
        ),

        ('Global Settings',
            {'fields': ('tenant', 'timezone',)}
        ),

        ('Permissions',
            {'fields': ('is_staff', 'groups',)}
        ),

        ('Billing Information',
            {'fields': ('billing_given_name', 'billing_last_name', 'billing_email')}
        ),

        ('Shipping Information',
            {'fields': ('shipping_given_name', 'shipping_last_name', 'shipping_email')}
        ),

        ('Email Activation / Password Reset',
            {'fields': ('was_email_activated', 'pr_access_code', 'pr_expiry_date')}
        ),

        ('Terms of Service',
            {'fields': ('has_signed_tos', 'tos_agreement', 'tos_signed_on')}
        ),
    )
    readonly_fields = []

    search_fields =  ['email',]
    ordering = ['email',]

    filter_horizontal = ()

admin.site.register(SharedUser, SharedUserAdmin)




class SharedGroupAdmin(admin.ModelAdmin):
    raw_id_fields = []
    list_filter = []
    list_display = ['name',]
    ordering = []
    readonly_fields = []

admin.site.register(SharedGroup, SharedGroupAdmin)
admin.site.unregister(Group) # Developers note: We want to user our proxy instead!

class SharedOrganizationAdmin(admin.ModelAdmin):
    raw_id_fields = []
    list_filter = []
    list_display = ['schema', 'name',]
    ordering = ['schema',]
    readonly_fields = [
        'id', 'created_at', 'created_by', 'created_from',
        'created_from_is_public', 'last_modified_at', 'last_modified_by',
        'last_modified_from', 'last_modified_from_is_public',
    ]


    def save_model(self, request, obj, form, change):
        """
        Override the `save` function in `Django Admin` to include audit details
        and the following additions:
        (1) Create our API token which the device will be using for making API
            calls to our service.
        """
        client_ip, is_routable = get_client_ip(request)
        obj.created_by = request.user
        obj.created_from = client_ip
        obj.created_from_is_public = is_routable
        obj.last_modified_by = request.user
        obj.last_modified_from = client_ip
        obj.last_modified_from_is_public = is_routable
        super().save_model(request, obj, form, change)

admin.site.register(SharedOrganization, SharedOrganizationAdmin)
