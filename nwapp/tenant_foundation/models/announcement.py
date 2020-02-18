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
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class AnnouncementManager(models.Manager):
    def delete_all(self):
        items = Announcement.objects.all()
        for item in items.all():
            item.delete()


class Announcement(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_announcements'
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        default_permissions = ()
        permissions = ()

    '''
    OBJECT MANAGERS
    '''

    objects = AnnouncementManager()

    '''
    MODEL FIELDS
    '''

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this announcement.'),
        db_index=True,
        unique=True
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether announcement was archived.'),
        default=False,
        blank=True,
        db_index=True
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
        related_name="created_announcements",
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
        related_name="last_modified_announcements",
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
            try:
                latest_obj = Announcement.objects.latest('id');
                self.id = latest_obj.id + 1
            except Announcement.DoesNotExist:
                self.id = 1

        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            slug = slugify(self.text)
            while Announcement.objects.filter(slug=slug).exists():
                slug = slugify(self.text)+"-"+get_referral_code(16)
            self.slug = Truncator(slug).chars(255)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Announcement, self).save(*args, **kwargs)
