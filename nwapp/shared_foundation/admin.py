from ipware import get_client_ip
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin

from shared_foundation.models import *


# Define a new SharedUser admin
class SharedUserAdmin(BaseUserAdmin):
    raw_id_fields = ['referred_by',]
    list_display = ['email', 'is_staff', 'is_active', 'was_email_activated',  'referred_by',]
    list_filter = ('is_staff',  'is_active', 'was_email_activated', )

    fieldsets = (
        (None,
            {'fields': ('email','password')}
        ),

        ('Global Settings',
            {'fields': ('timezone',)}
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
