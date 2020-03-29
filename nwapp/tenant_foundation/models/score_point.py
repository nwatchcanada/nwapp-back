# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser


class ScorePointManager(models.Manager):
    def delete_all(self):
        items = ScorePoint.objects.all()
        for item in items.all():
            item.delete()


class ScorePoint(models.Model):
    """
    Model to represent the score points awarded to the user for a specific task.
    This model is immutable once created and can only be 'archived' if deleted
    by the staff.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_score_points'
        verbose_name = _('Score Point')
        verbose_name_plural = _('Score Points')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        OTHER = 1
        DONATION = 2
        DAILY_USAGE = 3

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.DONATION, _('Neighbourhood Watch Donation')),
        (TYPE_OF.DAILY_USAGE, _('Daily Usage')),
        (TYPE_OF.OTHER, _('Other')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = ScorePointManager()

    '''
    MODEL FIELDS
    '''

    #  BUSINESS LOGIC FIELDS

    user = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom owns these score point.'),
        related_name="score_points",
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
        help_text=_('The custom description override by the staff if the `Other` type was selected for this score point.'),
        max_length=255,
        null=True,
        blank=True,
    )
    amount = models.PositiveSmallIntegerField(
        _("Amount"),
        help_text=_('The amount number awarded for this score point.'),
        blank=True,
        null=False,
        default=0,
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
        help_text=_('The tags associated with this score point.'),
        blank=True,
        related_name="score_points"
    )

    # SYSTEM FIELDS

    uuid = models.UUIDField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this unique score point.'),
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this score point.'),
        related_name="created_score_points",
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
        help_text=_('The user whom last modified this private image upload.'),
        related_name="last_modified_score_points",
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
                latest_obj = ScorePoint.objects.latest('id');
                self.id = latest_obj.id + 1
            except ScorePoint.DoesNotExist:
                self.id = 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(ScorePoint, self).save(*args, **kwargs)

    def get_type_of_label(self):
        if self.type_of == ScorePoint.TYPE_OF.OTHER:
            return self.type_of_other
        return str(dict(ScorePoint.TYPE_OF_CHOICES).get(self.type_of))

    def get_description(self):
        if self.type_of == ScorePoint.TYPE_OF.OTHER:
            return self.description_other
        elif self.type_of == ScorePoint.TYPE_OF.DONATION:
            return _("Score awarded for donating to Neighbourhood Watch.")
        elif self.type_of == ScorePoint.TYPE_OF.DAILY_USAGE:
            return _("Score awarded using service in a day.")

    @classmethod
    def award(cls, user, type_of, type_of_other, description_other, amount, created_by, last_modified_by):
        """
        Custom constructor used to create the object using `Pessimistic approach`
        method for handling locking and concurrency; furthermore, the user's
        score will get automatically updated.

        Special thanks: https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2
        """
        with transaction.atomic():
            # Create our award.
            score_point = cls.objects.select_for_update().create(
                user=user,
                type_of=type_of,
                type_of_other=type_of_other,
                description_other=description_other,
                amount=amount,
                created_by=created_by,
                last_modified_by=last_modified_by
            )

            # Update total score.
            user.score += amount
            user.save()

            # Return our new object.
            return score_point

    @classmethod
    def archive(cls, uuid, last_modified_by, last_modified_from, last_modified_from_is_public):
        """
        Custom constructor used to archive the object using `Pessimistic approach`
        method for handling locking and concurrency; furthermore, the user's
        score will get automatically updated.

        Special thanks: https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2
        """
        with transaction.atomic():
            # Create our award.
            score_point = cls.objects.select_for_update().get(
                uuid=uuid
            )
            score_point.is_archived = True
            score_point.last_modified_by = last_modified_by
            score_point.last_modified_from = last_modified_from
            score_point.last_modified_from_is_public = last_modified_from_is_public
            score_point.save()

            # Update total score.
            score_point.user.score -= score_point.amount
            score_point.user.save()

            # Return our new object.
            return score_point
