# -*- coding: utf-8 -*-
import csv
import pytz
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.gis.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.constants import *
from shared_foundation.models import SharedUser


class TaskItemManager(models.Manager):
    def delete_all(self):
        for obj in TaskItem.objects.iterator(chunk_size=500):
            obj.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return TaskItem.objects.filter(
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    todays_dt = timezone.now() + timedelta(days=days)
    return todays_dt.date()


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
        ASSIGN_ASSOCIATE_TO_DISTRICT = 3
        ACTION_INCIDENT_ITEM = 4
        ACTION_CONCERNT_ITEM = 5

    class STATE:
        UNASSIGNED = 1
        PENDING = 2
        CLOSED = 3

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH, _('Assign Area Coordinator to Watch')),
        (TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH, _('Assign Associate to Watch')),
        (TYPE_OF.ASSIGN_ASSOCIATE_TO_DISTRICT, _('Assign Associate to District')),
        (TYPE_OF.ACTION_INCIDENT_ITEM, _('Action a NW concern item')),
        (TYPE_OF.ACTION_CONCERNT_ITEM, _('Action a NW item item')),
    )

    STATE_CHOICES = (
        (STATE.UNASSIGNED, _('Unassigned')),
        (STATE.PENDING, _('Pending')),
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
    member = models.ForeignKey(
        "Member",
        help_text=_('The associate related to this task item.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    area_coordinator = models.ForeignKey(
        "AreaCoordinator",
        help_text=_('The area coordinator related to this task item.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate related to this task item.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    district = models.ForeignKey(
        "District",
        help_text=_('The district whom this task item belongs to.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch this task item belongs to.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    item = models.ForeignKey(
        "Item",
        help_text=_('The item this task item belongs to.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    staff = models.ForeignKey(
        "Staff",
        help_text=_('The staff member which is responsibel for processing this task item.'),
        related_name="task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this task item.'),
        blank=True,
        related_name="task_items"
    )

    next_task_item = models.ForeignKey(
        "self",
        help_text=_('The next task item that belongs to this task item.'),
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    previous_task_item = models.ForeignKey(
        "self",
        help_text=_('The previous task item that belongs to this task item.'),
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

    # SEARCHABLE FIELDS

    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=1023,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )

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

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(TaskItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_type_of_label()+" (External ID: "+str(self.uuid)+")"

    def get_type_of_label(self):
        return dict(TaskItem.TYPE_OF_CHOICES).get(self.type_of)

    def get_state_label(self):
        return dict(TaskItem.STATE_CHOICES).get(self.state)

    @staticmethod
    def get_searchable_content(task_item):
        """
        Utility function which refreshes the searchable content used when
        searching for `keywords`.
        """
        text = str(task_item.uuid) + " "
        text += task_item.get_type_of_label() + " "
        text += task_item.get_description()
        return str(text)

    def get_description(self):
        text = ""
        if self.type_of == self.TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH:
            text = _("A new watch has been created and requires an area coordinator to be assigned. Please assign an area coordinator to the watch.")
        elif self.type_of == self.TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH:
            text = _("A new watch has been created and requires an associate to be assigned. Please assign an associate to the watch.")
        elif self.type_of == self.TYPE_OF.ASSIGN_ASSOCIATE_TO_DISTRICT:
            text = _("A new district has been created and requires an associate to be assigned. Please assign an associate to the watch.")
        elif self.type_of == self.TYPE_OF.ACTION_INCIDENT_ITEM:
            text = _("Someone submitted a NW incident item that requires action.")
        elif self.type_of == self.TYPE_OF.ACTION_CONCERNT_ITEM:
            text = _("Someone submitted a NW concern item that requires action.")
        return str(text)

    @staticmethod
    def seed(tenant, length=25):
        from faker import Faker
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                from shared_foundation.models import SharedUser, SharedGroup
                type_of = faker.pyint(min_value=1, max_value=5, step=1)
                if type_of == TaskItem.TYPE_OF.ASSIGN_AREA_COORDINATOR_TO_WATCH or type_of == TaskItem.TYPE_OF.ASSIGN_ASSOCIATE_TO_WATCH:
                    from tenant_foundation.models import Watch

                    watch = Watch.objects.filter(
                        task_items__isnull=True
                    ).first()
                    random_days_count = faker.pyint(min_value=0, max_value=10, step=1)
                    task_item = TaskItem.objects.create(
                        type_of=type_of,
                        state=TaskItem.STATE.UNASSIGNED,
                        due_date=get_todays_date(random_days_count),
                        watch=watch,
                    )
                    results.append(task_item)

                elif type_of == TaskItem.TYPE_OF.ASSIGN_ASSOCIATE_TO_DISTRICT:
                    from tenant_foundation.models import Associate

                    associate = Associate.objects.random()
                    if associate:
                        random_days_count = faker.pyint(min_value=0, max_value=10, step=1)
                        task_item = TaskItem.objects.create(
                            type_of=type_of,
                            state=TaskItem.STATE.UNASSIGNED,
                            due_date=get_todays_date(random_days_count),
                            associate=associate,
                        )
                        results.append(task_item)

                elif type_of == TaskItem.TYPE_OF.ACTION_INCIDENT_ITEM or type_of == TaskItem.TYPE_OF.ACTION_CONCERNT_ITEM:
                    from tenant_foundation.models import Item

                    item = Item.objects.filter(
                        task_items__isnull=True
                    ).first()
                    random_days_count = faker.pyint(min_value=0, max_value=10, step=1)
                    task_item = TaskItem.objects.create(
                        type_of=type_of,
                        state=TaskItem.STATE.UNASSIGNED,
                        due_date=get_todays_date(random_days_count),
                        item=item,
                    )
                    results.append(task_item)

            except Exception as e:
                print(e)
                pass
        return results
