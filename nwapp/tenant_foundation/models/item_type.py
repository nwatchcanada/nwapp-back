# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser
from shared_foundation.utils.string import get_referral_code

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class ItemTypeManager(models.Manager):
    def delete_all(self):
        items = ItemType.objects.all()
        for item in items.all():
            item.delete()


class ItemType(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_item_types'
        verbose_name = _('Item Type')
        verbose_name_plural = _('Item Types')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class CATEGORY:
        INCIDENT = 2
        EVENT = 3
        CONCERN = 4
        INFORMATION = 5
        COMMUNITY_NEWS = 6
        VOLUNTEER = 7
        RESOURCE = 8

    '''
    CHOICES
    '''

    CATEGORY_CHOICES = (
        (CATEGORY.INCIDENT, _('Incident')),
        (CATEGORY.EVENT, _('Event')),
        (CATEGORY.CONCERN, _('Concern')),
        (CATEGORY.INFORMATION, _('Information')),
        (CATEGORY.COMMUNITY_NEWS, _('Community News')),
        (CATEGORY.VOLUNTEER, _('Volunteer')),
        (CATEGORY.RESOURCE, _('Resource')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = ItemTypeManager()

    '''
    MODEL FIELDS
    '''

    category = models.PositiveSmallIntegerField(
        _("Category"),
        help_text=_('The category this type of belongs to.'),
        choices=CATEGORY_CHOICES,
        db_index=True,
    )
    text = models.CharField(
        _("Text"),
        max_length=127,
        help_text=_('The text content of this item type.'),
        db_index=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this item type.'),
        blank=True,
        null=True,
        default='',
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether item type was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    # AUDITING FIELDS

    uuid = models.CharField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this unique record.'),
        default=uuid.uuid4,
        editable=False,
        max_length=63, # Do not change
        unique=True,
        db_index=True,
    )
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
        related_name="created_item_types",
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
    created_from_position = models.PointField(
        _("Created from position"),
        help_text=_('The latitude and longitude coordinates for the creator.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_item_types",
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
    last_modified_from_position = models.PointField(
        _("Last modified from position"),
        help_text=_('The latitude and longitude coordinates for the last modified user.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
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
            try:
                latest_obj = ItemType.objects.latest('id');
                self.id = latest_obj.id + 1
            except ItemType.DoesNotExist:
                self.id = 1

        '''
        The following code will generate a unique slug and if the slug
        is not unique in the database, then continue to try generating
        a unique slug until it is found.
        '''
        if self.slug == "" or self.slug == None:
            slug = slugify(self.text)
            while ItemType.objects.filter(slug=slug).exists():
                slug = slugify(self.text)+"-"+get_referral_code(16)
            self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(ItemType, self).save(*args, **kwargs)

    def get_category_label(self):
        return str(dict(ItemType.CATEGORY_CHOICES).get(self.category))
