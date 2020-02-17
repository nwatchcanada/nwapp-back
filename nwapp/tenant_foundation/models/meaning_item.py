# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.utils.string import get_referral_code


class MeaningItemManager(models.Manager):
    def delete_all(self):
        items = MeaningItem.objects.all()
        for item in items.all():
            item.delete()


class MeaningItem(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_meaning_items'
        verbose_name = _('What does NW mean to you Item')
        verbose_name_plural = _('What does NW mean to you Items')
        default_permissions = ()
        permissions = ()

    '''
    MODEL FIELDS
    '''

    objects = MeaningItemManager()

    """
    MODEL FUNCTIONS
    """

    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique identifier used externally.'),
        max_length=255,
        null=False,
        unique=True,
        db_index=True,
    )
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
        If we are creating a new row, then we will automatically increment the
        `id` field instead of relying on Postgres DB.
        '''
        if self.id == None:
            latest_obj = MeaningItem.objects.latest('id');
            self.id = 1 if latest_obj == None else latest_obj.id + 1

        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            slug = slugify(self.text)
            while MeaningItem.objects.filter(slug=slug).exists():
                slug = slugify(self.text)+"-"+get_referral_code(16)
            self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(MeaningItem, self).save(*args, **kwargs)
