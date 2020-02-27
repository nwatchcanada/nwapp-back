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
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser
from shared_foundation.utils.string import get_referral_code

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class ItemManager(models.Manager):
    def delete_all(self):
        items = Item.objects.all()
        for item in items.all():
            item.delete()


class Item(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_items'
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STATE:
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        ARCHIVED = 'archived'

    class SHOWN_TO_WHOM:
        GENERAL_PUBLIC = 2
        ALL_NW_STAFF = 3
        MY_WATCH_AREA = 4

    class WHO_NEWS_FOR:
        MY_CITY = 2
        MY_DISTRICT = 3
        MY_WATCH = 4

    class FORMAT_TYPE:
        LINK_RESOURCE_TYPE_OF = 2
        YOUTUBE_VIDEO_RESOURCE_TYPE_OF = 3
        IMAGE_RESOURCE_TYPE_OF = 4
        FILE_RESOURCE_TYPE_OF = 5
        UNSPECIFIED_TYPE_OF = 6

    '''
    CHOICES
    '''

    STATE_CHOICES = (
        (STATE.ACTIVE, _('Active')),
        (STATE.INACTIVE, _('Inactive')),
        (STATE.ARCHIVED, _('Archived')),
    )

    SHOWN_TO_WHOM_CHOICES = (
        (SHOWN_TO_WHOM.GENERAL_PUBLIC, _('General Public')),
        (SHOWN_TO_WHOM.ALL_NW_STAFF, _('All NW Staff')),
        (SHOWN_TO_WHOM.MY_WATCH_AREA, _('My Watch Area')),
    )

    WHO_NEWS_FOR_CHOICES = (
        (WHO_NEWS_FOR.MY_CITY, _('My City')),
        (WHO_NEWS_FOR.MY_DISTRICT, _('My District')),
        (WHO_NEWS_FOR.MY_WATCH, _('My Watch')),
    )

    FORMAT_TYPE_CHOICES = (
        (FORMAT_TYPE.LINK_RESOURCE_TYPE_OF, _('Link')),
        (FORMAT_TYPE.YOUTUBE_VIDEO_RESOURCE_TYPE_OF, _('YouTube Video')),
        (FORMAT_TYPE.IMAGE_RESOURCE_TYPE_OF, _('Image')),
        (FORMAT_TYPE.FILE_RESOURCE_TYPE_OF, _('File')),
        (FORMAT_TYPE.UNSPECIFIED_TYPE_OF, _('Unspecified')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = ItemManager()

    '''
    MODEL FIELDS
    '''

    # COMMON FIELDS

    state = models.CharField(
        _('State'),
        help_text=_('The state of this item.'),
        max_length=15,
        choices=STATE_CHOICES,
        default=STATE.ACTIVE,
        blank=True,
        db_index=True,
    )
    type_of = models.ForeignKey(
        "ItemType",
        help_text=_('The custom type of item this is.'),
        related_name="type_ofs",
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this item, if it has one.'),
        blank=True,
        null=True,
        default='',
    )
    is_archived = models.BooleanField( # DEPRECATED
        _("Is Archived"),
        help_text=_('Indicates whether item was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    # EVENT FIELDS

    start_at = models.DateTimeField(
        _("Start at"),
        help_text=_('The date and time this item will start if it is an event.'),
        blank=True,
        null=True,
    )
    is_all_day_event = models.BooleanField(
        _("Is all day event"),
        help_text=_('Is this event item full day?'),
        default=False,
        blank=True
    )
    finish_at = models.DateTimeField(
        _("Finish at"),
        help_text=_('The date and time this item will finish if it is an event.'),
        blank=True,
        null=True,
    )
    title = models.CharField( # Event / Incident / Concern
        _("Title"),
        max_length=63,
        help_text=_('The title of the item, if it has one.'),
        null=True,
        blank=True,
        default='',
    )
    external_url = models.URLField(
        _("External URL"),
        max_length=63,
        help_text=_('The URL for the item to reference an external address.'),
        null=True,
        blank=True,
        default='',
    )
    shown_to_whom = models.PositiveSmallIntegerField(
        _("Shown to whom?"),
        help_text=_('The person / organization that is allowed to view this item.'),
        choices=SHOWN_TO_WHOM_CHOICES,
        null=True,
        blank=True,
    )
    can_be_posted_on_social_media = models.BooleanField(
        _("Can be posted on Social Media?"),
        help_text=_('Has the poster allowed this item be posted on social media?'),
        blank=True,
        default=True,
    )
    logo_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The logo image of this item.'),
        related_name="logo_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # INCIDENT / CONCERN

    has_notified_authorities = models.BooleanField(
        _("Has notified authorities"),
        help_text=_('Has notified authorities?'),
        default=False,
        blank=True,
        null=True,
    )
    has_accept_authority_cooperation = models.BooleanField(
        _("Has accepted authority cooperation"),
        help_text=_('Has user agreed to the fact that NW can contact the local and federal police services?'),
        default=False,
        blank=True,
        null=True,
    )
    date = models.DateTimeField(
        _("Date"),
        help_text=_('The date this event occured.'),
        blank=True,
        null=True,
    )
    location = models.CharField( # Event / Incident / Concern
        _("Location"),
        max_length=127,
        help_text=_('The location of where this event occured.'),
        null=True,
        blank=True,
        default='',
    )

    # COMMUNITY NEWS

    who_news_for = models.PositiveSmallIntegerField(
        _("Who news for?"),
        help_text=_('Whome shall see this news item?'),
        choices=WHO_NEWS_FOR_CHOICES,
        null=True,
        blank=True,
    )

    # RESOURCE

    format_type = models.PositiveSmallIntegerField(
        _("Format Type"),
        help_text=_('The format type of resource.'),
        choices=FORMAT_TYPE_CHOICES,
        default=FORMAT_TYPE.UNSPECIFIED_TYPE_OF,
        blank=True,
        null=True,
    )
    embed_code = models.CharField( # Event / Incident / Concern
        _("Embed Code"),
        max_length=1023,
        help_text=_('The YouTube embed code for this item.'),
        null=True,
        blank=True,
        default='',
    )
    resource_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The resource image of this item.'),
        related_name="resource_image_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    resource_file = models.ForeignKey(
        "PrivateFileUpload",
        help_text=_('The resource file of this item.'),
        related_name="resource_file_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
        related_name="created_items",
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
        related_name="last_modified_items",
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
        from tenant_foundation.models.item_type import ItemType
        if self.type_of.category == ItemType.CATEGORY.EVENT:
            return self.title
        if self.type_of.category == ItemType.CATEGORY.INCIDENT:
            return self.title
        if self.type_of.category == ItemType.CATEGORY.CONCERN:
            return self.title
        if self.type_of.category == ItemType.CATEGORY.COMMUNITY_NEWS or self.type_of.category == ItemType.CATEGORY.VOLUNTEER:
            return Truncator(self.description).chars(63)
        if self.type_of.category == ItemType.CATEGORY.RESOURCE:
            if self.format_type == Item.FORMAT_TYPE.LINK_RESOURCE_TYPE_OF:
                return self.title
            if self.format_type == Item.FORMAT_TYPE.YOUTUBE_VIDEO_RESOURCE_TYPE_OF:
                return self.title
        return str(self.slug)

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
                latest_obj = Item.objects.latest('id');
                self.id = latest_obj.id + 1
            except Item.DoesNotExist:
                self.id = 1

        '''
        If we are creating a new model, then we will automatically increment the `id`.
        '''
        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            from tenant_foundation.models.item_type import ItemType
            if self.type_of.category == ItemType.CATEGORY.EVENT or self.type_of.category == ItemType.CATEGORY.INCIDENT or self.type_of.category == ItemType.CATEGORY.CONCERN:
                slug = slugify(self.title)
                while Item.objects.filter(slug=slug).exists():
                    slug = slugify(self.title)+"-"+get_referral_code(16)
                self.slug = slug
            else:
                self.slug = str(self.id)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Item, self).save(*args, **kwargs)
