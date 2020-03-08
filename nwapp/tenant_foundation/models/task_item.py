# -*- coding: utf-8 -*-
import csv
import pytz
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.constants import *
from shared_foundation.models import SharedUser


class TaskItemManager(models.Manager):
    def delete_all(self):
        for obj in TaskItem.objects.iterator(chunk_size=500):
            obj.delete()


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


@transaction.atomic
def increment_task_item_id_number():
    """Function will generate a unique big-int."""
    last_task_item = TaskItem.objects.all().order_by('id').last();
    if last_task_item:
        return last_task_item.id + 1
    return 1


class TaskItem(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_task_items'
        ordering = ['due_date']
        verbose_name = _('Task Item')
        verbose_name_plural = _('Task Items')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        ASSIGN_AREA_COORDINATOR_TO_WATCH = 1
        ASSIGN_ASSOCIATE_TO_WATCH = 2
        ACTION_INCIDENT_ITEM = 3
        ACTION_CONCERNT_ITEM = 4

    class STATE:
        ACTIVE = 1
        CLOSED = 2

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH, _('Assign Area Coordinator to Watch')),
        (TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH, _('Assign Associate to Watch')),
        (TYPE_OF.ACTION_INCIDENT_ITEM, _('Action a NW concern item')),
        (TYPE_OF.ACTION_CONCERNT_ITEM, _('Action a NW item item')),
    )

    STATE_CHOICES = (
        (STATE.ACTIVE, _('Active')),
        (STATE.CLOSED, _('Closed')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = TaskItemManager()

    '''
    MODEL FIELDS
    '''

    uuid = models.UUIDField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this task item.'),
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of task item.'),
        choices=STATE_CHOICES,
        db_index=True
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of task item this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True
    )
    due_date = models.DateField(
        _('Due Date'),
        help_text=_('The date that this task must be finished by.'),
        blank=True,
        default=get_todays_date,
        db_index=True
    )

    # closing_reason = models.PositiveSmallIntegerField(
    #     _("Closing Reason"),
    #     help_text=_('The reason for this task was closed.'),
    #     blank=True,
    #     null=True,
    #     default=0,
    # )

    # """
    # 2 - Quote was too high
    # 3 - Job completed by someone else
    # 4 - Job completed by Associate
    # 5 - Work no longer needed
    # 6 - Client not satisfied with Associate
    # 7 - Client did work themselves
    # 8 - No Associate available
    # 9 - Work environment unsuitable
    # 10 - Client did not return call
    # 11 - Associate did not have necessary equipment
    # 12 - Repair not possible
    # 13 - Could not meet deadline
    # 14 - Associate did not call client
    # 15 - Member issue
    # 16 - Client billing issue
    # else - {{ task_item.closing_reason_other }}
    # """
    # closing_reason_other = models.CharField(
    #     _("Closing Reason other"),
    #     help_text=_('A specific reason this task was closed.'),
    #     max_length=1024,
    #     blank=True,
    #     null=True,
    #     default='',
    # )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="created_task_items",
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
        help_text=_('The user whom last modified this order.'),
        related_name="last_modified_task_items",
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
        return str(self.title)

    def get_pretty_type_of(self):
        return dict(TYPE_OF_CHOICES).get(self.type_of)
