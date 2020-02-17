# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from sorl.thumbnail import ImageField
from django.conf import settings
from django.db import models
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


class PrivateImageUploadManager(models.Manager):
    def delete_all(self):
        items = PrivateImageUpload.objects.all()
        for item in items.all():
            item.delete()


class PrivateImageUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_private_image_uploads'
        verbose_name = _('Private Image Upload')
        verbose_name_plural = _('Private Image Uploads')
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

    objects = PrivateImageUploadManager()

    '''
    MODEL FIELDS
    '''

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
        related_name="private_image_uploads",
        on_delete=models.CASCADE,
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch whom this image belongs to.'),
        related_name="private_image_uploads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        "District",
        help_text=_('The district whom this image belongs to.'),
        related_name="private_image_uploads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image_file = ImageField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload image.'),
        storage=PrivateMediaStorage()
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether private image was archived.'),
        default=False,
        blank=True,
        db_index=True
    )


    #
    #  SYSTEM
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this image.'),
        related_name="created_private_image_uploads",
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
        related_name="last_modified_private_image_uploads",
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
            latest_obj = PrivateImageUpload.objects.latest('id');
            self.id = 1 if latest_obj == None else latest_obj.id + 1

        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        slug = self.user.slug
        while PrivateImageUpload.objects.filter(slug=slug).exists():
            slug = self.user.slug+"-"+get_referral_code(16)
        self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(PrivateImageUpload, self).save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """
            Overrided delete functionality to include deleting the s3 image
            that we have stored on the system. Currently the deletion funciton
            is missing this functionality as it's our responsibility to handle
            the local images.
        """
        if self.data_image:
            self.data_image.delete()

        super(PrivateImageUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
