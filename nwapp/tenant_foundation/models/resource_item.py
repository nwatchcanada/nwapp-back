# -*- coding: utf-8 -*-
import csv
import pytz
import uuid
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
    CONSTANTS
    '''

    class TYPE_OF:
        LINK_RESOURCE_TYPE_OF = 2
        YOUTUBE_VIDEO_RESOURCE_TYPE_OF = 3
        IMAGE_RESOURCE_TYPE_OF = 4
        FILE_RESOURCE_TYPE_OF = 5

    class CATEGORY:
        HEALTH_RESOURCE_CATEGORY = 2
        HOUSING_RESOURCE_CATEGORY = 3
        LONELINESS_RESOURCE_CATEGORY = 4
        FOOD_AND_NUTRITION_RESOUCE_CATEGORY = 5
        EDUCATION_RESOURCE_CATEGORY = 6
        MUNICIPAL_RESOURCE_CATEGORY = 7
        POLICE_RESOURCE_CATEGORY = 8
        FIRE_RESOURCE_CATEGORY = 9
        EMERGENCY_RESOURCE_CATEGORY = 10

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.LINK_RESOURCE_TYPE_OF, _('Link')),
        (TYPE_OF.YOUTUBE_VIDEO_RESOURCE_TYPE_OF, _('YouTube Video')),
        (TYPE_OF.IMAGE_RESOURCE_TYPE_OF, _('Image')),
        (TYPE_OF.FILE_RESOURCE_TYPE_OF, _('File')),
    )

    CATEGORY_CHOICES = (
        (CATEGORY.HEALTH_RESOURCE_CATEGORY, _('Health')),
        (CATEGORY.HOUSING_RESOURCE_CATEGORY, _('Housing')),
        (CATEGORY.LONELINESS_RESOURCE_CATEGORY, _('Loneliness')),
        (CATEGORY.FOOD_AND_NUTRITION_RESOUCE_CATEGORY, _('Food and Nutrition')),
        (CATEGORY.EDUCATION_RESOURCE_CATEGORY, _('Education')),
        (CATEGORY.MUNICIPAL_RESOURCE_CATEGORY, _('Municipal')),
        (CATEGORY.POLICE_RESOURCE_CATEGORY, _('Police')),
        (CATEGORY.FIRE_RESOURCE_CATEGORY, _('Fire')),
        (CATEGORY.EMERGENCY_RESOURCE_CATEGORY, _('Emergency')),
    )


    '''
    OBJECT MANAGERS
    '''

    objects = ResourceItemManager()

    '''
    MODEL FIELDS
    '''

    category = models.PositiveSmallIntegerField(
        _("Category"),
        help_text=_('The type of score point this is.'),
        choices=CATEGORY_CHOICES,
        db_index=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of score point this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The the name of this resource item.'),
        db_index=True,
        unique=True
    )
    external_url = models.URLField(
        _("External URL"),
        help_text=_('The external website link of this resource item.'),
        max_length=255,
        null=True,
        blank=True,
    )
    embed_code = models.TextField(
        _("Embed Code"),
        help_text=_('The embed code of this resource item.'),
        null=True,
        blank=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('The description of this resource item.'),
        null=True,
        blank=True,
    )
    image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The image of this resource item.'),
        related_name="resource_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    file = models.ForeignKey(
        "PrivateFileUpload",
        help_text=_('The file of this resource item.'),
        related_name="resource_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether resource item was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    # AUDITING FIELDS

    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique identifier used externally.'),
        null=False,
        unique=True,
        db_index=True,
        max_length=255,
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
        If we are creating a new row, then we will automatically increment the
        `id` field instead of relying on Postgres DB.
        '''
        if self.id == None:
            latest_obj = ResourceItem.objects.latest('id');
            self.id = 1 if latest_obj == None else latest_obj.id + 1

        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            slug = slugify(self.name)
            while ResourceItem.objects.filter(slug=slug).exists():
                slug = slugify(self.name)+"-"+get_referral_code(4)
            self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(ResourceItem, self).save(*args, **kwargs)

    def get_type_of_label(self):
        return str(dict(ResourceItem.TYPE_OF_CHOICES).get(self.type_of))

    def get_category_label(self):
        return str(dict(ResourceItem.CATEGORY_CHOICES).get(self.category))
