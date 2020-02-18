# -*- coding: utf-8 -*-
import uuid
import pytz
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


class BadgeManager(models.Manager):
    def delete_all(self):
        items = Badge.objects.all()
        for item in items.all():
            item.delete()


class Badge(models.Model):
    """
    Model to represent the trophy badgeed to the user for a specific task.
    This model is immutable once created and can only be 'archived' if deleted
    by the staff.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_badges'
        verbose_name = _('Badge')
        verbose_name_plural = _('Badges')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
        )

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        OTHER = 1
        SUPPORTER = 2

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.SUPPORTER, _('Neighbourhood Watch Supporter')),
        (TYPE_OF.OTHER, _('Other')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = BadgeManager()

    '''
    MODEL FIELDS
    '''

    #  BUSINESS LOGIC FIELDS

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)#TODO: DELETE!!
    user = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom owns these score point.'),
        related_name="badges",
        on_delete=models.CASCADE,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of score point this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    type_of_other = models.CharField(
        _("Type of (Other)"),
        max_length=63,
        help_text=_('The specific description of the type of score point this is.'),
        blank=True,
        null=True,
    )
    description_other = models.CharField(
        _("Description (Other)"),
        help_text=_('The custom description override by the staff if the `Other` type was selected for this badge.'),
        max_length=255,
        null=True,
        blank=True,
    )
    icon = models.CharField(
        _("Icon"),
        max_length=64,
        help_text=_('The (fontawesome) icon used to describe this badge.'),
    )
    colour = models.CharField(
        _("Colour"),
        max_length=64,
        help_text=_('The colour of the badge.'),
    )
    description_other = models.CharField(
        _("Description (Other)"),
        max_length=255,
        help_text=_('The specific description for this badge.'),
        blank=True,
        null=True,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether score point was archived and not applied to the user\'s total score.'),
        default=False,
        blank=True,
        db_index=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this badge.'),
        blank=True,
        related_name="badges"
    )

    # SYSTEM FIELDS

    uuid = models.UUIDField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this unique badge.'),
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this score point.'),
        related_name="created_badges",
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
        related_name="last_modified_badges",
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
        return "Badge UUID: " + str(self.uuid)

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
                latest_obj = Badge.objects.latest('id');
                self.id = latest_obj.id + 1
            except Announcement.DoesNotExist:
                self.id = 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Badge, self).save(*args, **kwargs)

    def get_type_of_label(self):
        if self.type_of == Badge.TYPE_OF.OTHER:
            return self.type_of_other
        elif self.type_of == Badge.TYPE_OF.SUPPORTER:
            return _("Supporter")
        return None

    def get_description(self):
        if self.type_of == Badge.TYPE_OF.OTHER:
            return self.type_of_other
        elif self.type_of == Badge.TYPE_OF.SUPPORTER:
            return _("Badge given to users whom generously supported Neighbourhood Watch with financial donations")
