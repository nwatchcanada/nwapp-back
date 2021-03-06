# -*- coding: utf-8 -*-
import uuid
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from sorl.thumbnail import ImageField
from django.conf import settings
from django.contrib.gis.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from shared_foundation.models import SharedUser
from nwapp.s3utils import PrivateMediaStorage
from shared_foundation.utils.string import get_referral_code


class PrivateFileUploadManager(models.Manager):
    def delete_all(self):
        items = PrivateFileUpload.objects.all()
        for item in items.all():
            item.delete()


class PrivateFileUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_private_file_uploads'
        verbose_name = _('Private File Upload')
        verbose_name_plural = _('Private File Uploads')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    # class MEMBER_STATE:
    #     ACTIVE = 'active'
    #     INACTIVE = 'inactive'

    '''
    CHOICES
    '''

    # MEMBER_STATE_CHOICES = (
    #     (MEMBER_STATE.ACTIVE, _('Active')),
    #     (MEMBER_STATE.INACTIVE, _('Inactive')),
    # )

    '''
    OBJECT MANAGERS
    '''

    objects = PrivateFileUploadManager()

    '''
    MODEL FIELDS
    '''

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
        null=False,
        unique=True,
        db_index=True,
        max_length=255,
    )
    user = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom this belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.CASCADE,
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        "District",
        help_text=_('The district whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    item = models.ForeignKey(
        "Item",
        help_text=_('The items whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    data_file = models.FileField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload binary file.'),
        storage=PrivateMediaStorage()
    )
    title = models.CharField(
        _("Title"),
        max_length=63,
        help_text=_('The file title of this upload.'),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('The text content of this upload.'),
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this private file uploads.'),
        blank=True,
        related_name="private_file_uploads"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether private file was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=511,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )


    #
    #  SYSTEM
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this file.'),
        related_name="created_private_file_uploads",
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
        help_text=_('The user whom last modified this private file upload.'),
        related_name="last_modified_private_file_uploads",
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
        return str(self.pk)

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
                latest_obj = PrivateFileUpload.objects.latest('id');
                self.id = latest_obj.id + 1
            except PrivateFileUpload.DoesNotExist:
                self.id = 1

        if self.title == None:
            self.title = str(self.data_file)

        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        slug = self.user.slug
        while PrivateFileUpload.objects.filter(slug=slug).exists():
            slug = self.user.slug+"-"+get_referral_code(16)
        self.slug = slug

        search_text = str(self.slug)
        if self.title:
            search_text += " " + self.title
        if self.description:
            search_text += " " + self.description
        if self.data_file:
            search_text += " " + str(self.data_file)
        self.indexed_text = Truncator(search_text).chars(511)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(PrivateFileUpload, self).save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """
            Overrided delete functionality to include deleting the s3 file
            that we have stored on the system. Currently the deletion funciton
            is missing this functionality as it's our responsibility to handle
            the local files.
        """
        if self.data_file:
            self.data_file.delete()

        super(PrivateFileUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
