# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser, e164_phone_regex


class DistrictManager(models.Manager):
    def delete_all(self):
        items = District.objects.all()
        for item in items.all():
            item.delete()


class District(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_districts'
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        # ordering = ['-created_at']
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        RESIDENTIAL = 1
        BUSINESS = 2
        COMMUNITY_CARES = 3

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.RESIDENTIAL, _('Residential')),
        (TYPE_OF.BUSINESS, _('Business')),
        (TYPE_OF.COMMUNITY_CARES, _('Community Cares')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = DistrictManager()

    '''
    MODEL FIELDS
    '''

    #  COMMON FIELDS

    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of score point this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=127,
        help_text=_('The name of this district.'),
        unique=True,
        db_index=True,
    )
    description = models.CharField(
        _("Description"),
        help_text=_('The description of this district.'),
        max_length=255,
        null=True,
        blank=True,
    )

    # RESIDENTIAL FIELDS

    counselor_name = models.CharField(
        _("Counselor Name"),
        help_text=_('The name of this district\'s counselor.'),
        max_length=127,
        null=True,
        blank=True,
    )
    counselor_email = models.EmailField(
        _("Counselor Email"),
        help_text=_('The email of this district\'s counselor.'),
        max_length=127,
        null=True,
        blank=True,
    )
    counselor_phone = models.CharField(
        _("Counselor Phone"),
        help_text=_('The phone of this district\'s counselor.'),
        max_length=31,
        validators=[e164_phone_regex],
        null=True,
        blank=True,
    )

    # BUSINESS FIELDS

    website_url = models.URLField(
        _("Website URL"),
        help_text=_('The external website link of this district.'),
        max_length=255,
        null=True,
        blank=True,
    )
    logo_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The logo image of this district.'),
        related_name="districts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # SYSTEM FIELDS

    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique identifier used externally.'),
        max_length=255,
        null=False,
        unique=True,
        db_index=True,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether district was archived or not'),
        default=False,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this score point.'),
        related_name="created_districts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
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
        help_text=_('The user whom last modified this private image upload.'),
        related_name="last_modified_districts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
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
        return "District UUID: " + str(self.uuid)

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        if self.slug == None or self.slug == "":
            self.slug = slugify(self.name)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(District, self).save(*args, **kwargs)
