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

from shared_foundation.models import SharedUser
from shared_foundation.utils.string import get_referral_code

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class StreetAddressRangeManager(models.Manager):
    def delete_all(self):
        items = StreetAddressRange.objects.all()
        for item in items.all():
            item.delete()


class StreetAddressRange(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_street_address_ranges'
        verbose_name = _('Street Address Range')
        verbose_name_plural = _('Street Address Ranges')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STREET_TYPE:
        OTHER = 1
        AVENUE = 2
        DRIVE = 3
        ROAD = 4
        STREET = 5
        WAY = 6

    class STREET_DIRECTION:
        NONE = 0
        EAST = 1
        NORTH = 2
        NORTH_EAST = 3
        NORTH_WEST = 4
        SOUTH = 5
        SOUTH_EAST = 6
        SOUTH_WEST = 7
        WEST = 8

    '''
    CHOICES
    '''

    STREET_TYPE_CHOICES = (
        (STREET_TYPE.AVENUE, _('Avenue')),
        (STREET_TYPE.DRIVE, _('Drive')),
        (STREET_TYPE.ROAD, _('Road')),
        (STREET_TYPE.STREET, _('Street')),
        (STREET_TYPE.WAY, _('Way')),
        (STREET_TYPE.OTHER, _('Other')),
    )

    STREET_DIRECTION_CHOICES = (
        (STREET_DIRECTION.NONE, _('-')),
        (STREET_DIRECTION.EAST, _('East')),
        (STREET_DIRECTION.NORTH, _('North')),
        (STREET_DIRECTION.NORTH_EAST, _('North East')),
        (STREET_DIRECTION.NORTH_WEST, _('North West')),
        (STREET_DIRECTION.SOUTH, _('South')),
        (STREET_DIRECTION.SOUTH_EAST, _('South East')),
        (STREET_DIRECTION.SOUTH_WEST, _('South West')),
        (STREET_DIRECTION.WEST, _('West')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = StreetAddressRangeManager()

    '''
    MODEL FIELDS
    '''

    street_number_start = models.PositiveSmallIntegerField(
        _("Street Number Start"),
        help_text=_('Please select the street number start range.'),
    )
    street_number_end = models.PositiveSmallIntegerField(
        _("Street Number End"),
        help_text=_('Please select the street number end range.'),
    )
    street_name = models.CharField(
        _("Street Name"),
        max_length=63,
        help_text=_('The name of the street.'),
        db_index=True,
        unique=True
    )
    street_type = models.PositiveSmallIntegerField(
        _("Street Type"),
        help_text=_('Please select the street type.'),
        choices=STREET_TYPE_CHOICES,
    )
    street_type_other = models.CharField(
        _("Street Type (Other)"),
        max_length=127,
        help_text=_('Please select the street type not listed in our types.'),
        null=True,
        blank=True,
    )
    street_direction = models.PositiveSmallIntegerField(
        _("Street Direction"),
        help_text=_('Please select the street direction.'),
        choices=STREET_DIRECTION_CHOICES,
        blank=True,
        default=STREET_DIRECTION.NONE,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether tag was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch whom this street address range belongs to.'),
        related_name="street_address_ranges",
        on_delete=models.CASCADE,
    )

    # AUDITING FIELDS

    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique identifier used externally.'),
        max_length=255,
        null=False,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_street_address_ranges",
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
        related_name="last_modified_street_address_ranges",
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
        If we are creating a new model, then we will automatically increment the `id`.
        '''
        # # The following code will generate a unique slug and if the slug
        # # is not unique in the database, then continue to try generating
        # # a unique slug until it is found.
        # if self.slug == "" or self.slug == None:
        #     slug = slugify(self.text)
        #     while StreetAddressRange.objects.filter(slug=slug).exists():
        #         slug = slugify(self.text)+"-"+get_referral_code(16)
        #     self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(StreetAddressRange, self).save(*args, **kwargs)