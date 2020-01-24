# -*- coding: utf-8 -*-
import csv
import pytz
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class ResourceItemManager(models.Manager):
    def delete_all(self):
        items = ResourceItem.objects.all()
        for item in items.all():
            item.delete()


class ResourceItem(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_resource_items'
        verbose_name = _('Resource Item')
        verbose_name_plural = _('Resource Items')
        default_permissions = ()
        permissions = ()

    '''
    OBJECT MANAGERS
    '''

    objects = ResourceItemManager()

    '''
    MODEL FIELDS
    '''

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this resource item.'),
        db_index=True,
        unique=True
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether resource item was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    # AUDITING FIELDS

    uuid = models.UUIDField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this resource item.'),
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_resource_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_resource_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    """
    MODEL FUNCTIONS
    """

    def __str__(self):
        return str(self.text)

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(ResourceItem, self).save(*args, **kwargs)
