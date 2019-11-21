# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ExpectationItemManager(models.Manager):
    def delete_all(self):
        items = ExpectationItem.objects.all()
        for item in items.all():
            item.delete()


class ExpectationItem(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_expectation_items'
        verbose_name = _('What do you expect from NW Item')
        verbose_name_plural = _('What do you expect from NW Items')
        default_permissions = ()
        permissions = ()

    '''
    MODEL FIELDS
    '''

    objects = ExpectationItemManager()

    """
    MODEL FUNCTIONS
    """

    text = models.CharField(
        _("Text"),
        max_length=127,
        help_text=_('The text content of this item.'),
        db_index=True,
        unique=True
    )
    sort_number = models.PositiveSmallIntegerField(
        _("Sort #"),
        help_text=_('The number this item will appear when sorted by number.'),
        blank=True,
        default=0,
        db_index=True,
    )
    is_for_associate = models.BooleanField(
        _("Is for associate"),
        help_text=_('Indicates this option will be visible for the associate.'),
        default=True,
        blank=True
    )
    is_for_customer = models.BooleanField(
        _("Is for customer"),
        help_text=_('Indicates this option will be visible for the customer.'),
        default=True,
        blank=True
    )
    is_for_staff = models.BooleanField(
        _("Is for staff"),
        help_text=_('Indicates this option will be visible for the staff.'),
        default=True,
        blank=True
    )
    is_for_partner = models.BooleanField(
        _("Is for partner"),
        help_text=_('Indicates this option will be visible for the partner.'),
        default=True,
        blank=True
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether how hear item was archived.'),
        default=False,
        blank=True,
        db_index=True
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
        If we are creating a new model, then we will automatically increment the `id`.
        '''
        if self.id == 0 or self.id == None:
            self.id = ExpectationItem.objects.count() + 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(ExpectationItem, self).save(*args, **kwargs)
