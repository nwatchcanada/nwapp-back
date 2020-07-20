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


class AreaCoordinatorCommentManager(models.Manager):
    def delete_all(self):
        items = AreaCoordinatorComment.objects.all()
        for item in items.all():
            item.delete()


class AreaCoordinatorComment(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_area_coordinator_comments'
        verbose_name = _('Area Coordinator Comment')
        verbose_name_plural = _('Area Coordinator Comments')
        ordering = ['-created_at']
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

    objects = AreaCoordinatorCommentManager()

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
    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment this item belongs to.'),
        related_name="area_coordinator_comments",
        on_delete=models.CASCADE,
    )
    area_coordinator = models.ForeignKey(
        "AreaCoordinator",
        help_text=_('The area coordinator whom this comment is about.'),
        related_name="area_coordinator_comments",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    """
    MODEL FUNCTIONS
    """

    def __str__(self):
        return str(self.area_coordinator)+" "+str(self.created_at)

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
                latest_obj = AreaCoordinatorComment.objects.latest('id');
                self.id = latest_obj.id + 1
            except AreaCoordinatorComment.DoesNotExist:
                self.id = 1

        if self.slug == None or self.slug == "":
            # The following code will generate a unique slug and if the slug
            # is not unique in the database, then continue to try generating
            # a unique slug until it is found.
            slug = self.area_coordinator.user.slug
            while AreaCoordinatorComment.objects.filter(slug=slug).exists():
                slug = self.area_coordinator.user.slug+"-"+get_referral_code(4)
            self.slug = slug

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(AreaCoordinatorComment, self).save(*args, **kwargs)
