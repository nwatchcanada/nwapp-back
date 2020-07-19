# -*- coding: utf-8 -*-
import csv
import pytz
import string
import random
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.gis.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator

from shared_foundation.constants import *
from shared_foundation.models import SharedUser, SharedGroup


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class UnifiedSearchItemManager(models.Manager):
    def delete_all(self):
        items = UnifiedSearchItem.objects.all()
        for item in items.all():
            item.delete()

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return UnifiedSearchItem.objects.filter(
            Q(text__icontains=keyword) |
            Q(text__istartswith=keyword) |
            Q(text__iendswith=keyword) |
            Q(text__exact=keyword) |
            Q(text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return UnifiedSearchItem.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)

    def update_or_create_member(self, member):
        if member is None:
            return None, False

        indexed_text = member.indexed_text
        if indexed_text is None or indexed_text is "":
            indexed_text = get_random_string(32)

        item = UnifiedSearchItem.objects.filter(member__user=member.user).first()
        if item is not None:
            was_created = False

            # item.slug=member.user.slug+"-"+get_random_string(16)
            item.type_of=UnifiedSearchItem.get_type_of_member(member)
            item.member=member
            item.description=str(member)
            item.text=indexed_text
            item.created_at=member.created_at
            item.created_by=member.created_by
            item.created_from=member.created_from
            item.created_from_is_public=member.created_from_is_public
            item.last_modified_at=member.last_modified_at
            item.last_modified_by=member.last_modified_by
            item.last_modified_from=member.last_modified_from
            item.last_modified_from_is_public=member.last_modified_from_is_public
            item.save()
        else:
            item = UnifiedSearchItem.objects.create(
                slug=member.user.slug+"-"+get_random_string(16),
                type_of=UnifiedSearchItem.get_type_of_member(member),
                member=member,
                description=str(member),
                text=indexed_text,
                created_at=member.created_at,
                created_by=member.created_by,
                created_from=member.created_from,
                created_from_is_public=member.created_from_is_public,
                last_modified_at=member.last_modified_at,
                last_modified_by=member.last_modified_by,
                last_modified_from=member.last_modified_from,
                last_modified_from_is_public=member.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(member.metric.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_area_coordinator(self, area_coordinator):
        indexed_text = area_coordinator.indexed_text
        if indexed_text is None or indexed_text is "":
            indexed_text = get_random_string(32)
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(area_coordinator=area_coordinator)
            # item.slug=area_coordinator.user.slug+"-"+get_random_string(16)
            item.type_of=UnifiedSearchItem.TYPE_OF.AREA_COORDINATOR
            item.area_coordinator=area_coordinator
            item.description=str(area_coordinator)
            item.text=indexed_text
            item.created_at=area_coordinator.created_at
            item.created_by=area_coordinator.created_by
            item.created_from=area_coordinator.created_from
            item.created_from_is_public=area_coordinator.created_from_is_public
            item.last_modified_at=area_coordinator.last_modified_at
            item.last_modified_by=area_coordinator.last_modified_by
            item.last_modified_from=area_coordinator.last_modified_from
            item.last_modified_from_is_public=area_coordinator.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=area_coordinator.user.slug+get_random_string(16),
                type_of=UnifiedSearchItem.TYPE_OF.AREA_COORDINATOR,
                area_coordinator=area_coordinator,
                description=str(area_coordinator),
                text=indexed_text,
                created_at=area_coordinator.created_at,
                created_by=area_coordinator.created_by,
                created_from=area_coordinator.created_from,
                created_from_is_public=area_coordinator.created_from_is_public,
                last_modified_at=area_coordinator.last_modified_at,
                last_modified_by=area_coordinator.last_modified_by,
                last_modified_from=area_coordinator.last_modified_from,
                last_modified_from_is_public=area_coordinator.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(area_coordinator.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_associate(self, associate):
        indexed_text = associate.indexed_text
        if indexed_text is None or indexed_text is "":
            indexed_text = get_random_string(32)

        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(associate=associate)
            # item.slug = associate.user.slug+"-"+get_random_string(16)
            item.type_of=UnifiedSearchItem.TYPE_OF.ASSOCIATE
            item.description=str(associate)
            item.associate=associate
            item.text=indexed_text
            item.created_at=associate.created_at
            item.created_by=associate.created_by
            item.created_from=associate.created_from
            item.created_from_is_public=associate.created_from_is_public
            item.last_modified_at=associate.last_modified_at
            item.last_modified_by=associate.last_modified_by
            item.last_modified_from=associate.last_modified_from
            item.last_modified_from_is_public=associate.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=associate.user.slug+"-"+get_random_string(16),
                type_of=UnifiedSearchItem.TYPE_OF.ASSOCIATE,
                associate=associate,
                description=str(associate),
                text=indexed_text,
                created_at=associate.created_at,
                created_by=associate.created_by,
                created_from=associate.created_from,
                created_from_is_public=associate.created_from_is_public,
                last_modified_at=associate.last_modified_at,
                last_modified_by=associate.last_modified_by,
                last_modified_from=associate.last_modified_from,
                last_modified_from_is_public=associate.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(associate.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_staff(self, staff):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(staff=staff)
            item.slug = staff.user.slug
            item.type_of=UnifiedSearchItem.TYPE_OF.STAFF
            item.staff=staff
            item.description=str(staff)
            item.text=staff.indexed_text
            item.created_at=staff.created_at
            item.created_by=staff.created_by
            item.created_from=staff.created_from
            item.created_from_is_public=staff.created_from_is_public
            item.last_modified_at=staff.last_modified_at
            item.last_modified_by=staff.last_modified_by
            item.last_modified_from=staff.last_modified_from
            item.last_modified_from_is_public=staff.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=staff.user.slug,
                type_of=UnifiedSearchItem.TYPE_OF.STAFF,
                staff=staff,
                description=str(staff),
                text=staff.indexed_text,
                created_at=staff.created,
                created_by=staff.created_by,
                created_from=staff.created_from,
                created_from_is_public=staff.created_from_is_public,
                last_modified_at=staff.last_modified_at,
                last_modified_by=staff.last_modified_by,
                last_modified_from=staff.last_modified_from,
                last_modified_from_is_public=staff.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(staff.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_item(self, item):
        try:
            was_created = False
            found_item = UnifiedSearchItem.objects.get(item=item)
            found_item.slug = item.slug
            found_item.type_of=UnifiedSearchItem.TYPE_OF.ITEM
            found_item.item=item
            found_item.description="Work Order #"+str(item.id)
            found_item.text=item.indexed_text
            found_item.created_at=item.created_at
            found_item.created_by=item.created_by
            found_item.created_from=item.created_from
            found_item.created_from_is_public=item.created_from_is_public
            found_item.last_modified_at=item.last_modified_at
            found_item.last_modified_by=item.last_modified_by
            found_item.last_modified_from=item.last_modified_from
            found_item.last_modified_from_is_public=item.last_modified_from_is_public
            found_item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.TYPE_OF.ITEM,
                slug=slug,
                item=item,
                description="Work Order #"+str(item.id),
                text=item.indexed_text,
                created_at=item.created_at,
                created_by=item.created_by,
                created_from=item.created_from,
                created_from_is_public=item.created_from_is_public,
                last_modified_at=item.last_modified_at,
                last_modified_by=item.last_modified_by,
                last_modified_from=item.last_modified_from,
                last_modified_from_is_public=item.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(item.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_watch(self, watch):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(watch=watch)
            item.slug = watch.slug
            item.type_of=UnifiedSearchItem.TYPE_OF.WATCH
            item.watch=watch
            item.description=str(watch)
            item.text=watch.indexed_text
            item.created_at=watch.created_at
            item.created_by=watch.created_by
            item.created_from=watch.created_from
            item.created_from_is_public=watch.created_from_is_public
            item.last_modified_at=watch.last_modified_at
            item.last_modified_by=watch.last_modified_by
            item.last_modified_from=watch.last_modified_from
            item.last_modified_from_is_public=watch.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=watch.slug,
                type_of=UnifiedSearchItem.TYPE_OF.WATCH,
                watch=watch,
                description=str(watch),
                text=watch.indexed_text,
                created_at=watch.created_at,
                created_by=watch.created_by,
                created_from=watch.created_from,
                created_from_is_public=watch.created_from_is_public,
                last_modified_at=watch.last_modified_at,
                last_modified_by=watch.last_modified_by,
                last_modified_from=watch.last_modified_from,
                last_modified_from_is_public=watch.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(watch.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_district(self, district):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(district=district)
            item.slug = district.slug
            item.type_of=UnifiedSearchItem.TYPE_OF.DISTRICT
            item.district=district
            item.description=str(district)
            item.text=district.indexed_text
            item.created_at=district.created
            item.created_by=district.created_by
            item.created_from=district.created_from
            item.created_from_is_public=district.created_from_is_public
            item.last_modified_at=district.last_modified
            item.last_modified_by=district.last_modified_by
            item.last_modified_from=district.last_modified_from
            item.last_modified_from_is_public=district.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=district.slug,
                type_of=UnifiedSearchItem.TYPE_OF.DISTRICT,
                district=district,
                description=str(district),
                text=district.indexed_text,
                created_at=district.created,
                created_by=district.created_by,
                created_from=district.created_from,
                created_from_is_public=district.created_from_is_public,
                last_modified_at=district.last_modified,
                last_modified_by=district.last_modified_by,
                last_modified_from=district.last_modified_from,
                last_modified_from_is_public=district.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(district.tags.all())
        except Exception as e:
            pass

        return item, was_created

    def update_or_create_file(self, file):
        try:
            item = UnifiedSearchItem.objects.get(file=file)
            item.slug = file.slug
            item.type_of=UnifiedSearchItem.TYPE_OF.FILE
            item.file=file
            item.description=str(file)
            item.text=file.indexed_text
            item.created_at=file.created_at
            item.created_by=file.created_by
            item.created_from=file.created_from
            item.created_from_is_public=file.created_from_is_public
            item.last_modified_at=file.last_modified_at
            item.last_modified_by=file.last_modified_by
            item.last_modified_from=file.last_modified_from
            item.last_modified_from_is_public=file.last_modified_from_is_public
            item.save()
            was_created = False
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                slug=file.slug,
                type_of=UnifiedSearchItem.TYPE_OF.FILE,
                file=file,
                description=str(file),
                text=file.indexed_text,
                created_at=file.created_at,
                created_by=file.created_by,
                created_from=file.created_from,
                created_from_is_public=file.created_from_is_public,
                last_modified_at=file.last_modified_at,
                last_modified_by=file.last_modified_by,
                last_modified_from=file.last_modified_from,
                last_modified_from_is_public=file.last_modified_from_is_public,
            )
            was_created = True

        try:
            item.tags.set(file.tags.all())
        except Exception as e:
            pass

        return item, was_created


class UnifiedSearchItem(models.Model):

    """
    META
    """

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_unified_search_items'
        verbose_name = _('Unified Search Item')
        verbose_name_plural = _('Unified Search Items')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        MEMBER = 1
        AREA_COORDINATOR = 2
        ASSOCIATE = 3
        STAFF = 4
        ITEM = 5
        WATCH = 6
        DISTRICT = 7
        FILE = 8

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.MEMBER, _('Customer')),
        (TYPE_OF.AREA_COORDINATOR, _('Area Coordinator')),
        (TYPE_OF.ASSOCIATE, _('Associate')),
        (TYPE_OF.STAFF, _('Staff')),
        (TYPE_OF.ITEM, _('Item')),
        (TYPE_OF.WATCH, _('Watch')),
        (TYPE_OF.DISTRICT, _('District')),
        (TYPE_OF.FILE, _('File')),
    )

    """
    OBJECT MANAGER
    """

    objects = UnifiedSearchItemManager()

    """
    FIELDS
    """

    # THE FOLLOWING FIELDS ARE USED FOR SEARCHING.

    text = models.CharField(
        _("Text"),
        max_length=2047,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags with this unified search item.'),
        blank=True,
        related_name="unified_search_items"
    )

    # THE FOLLOWING FIELDS ARE USED TO MAP OUR SEARCHABLE ITEM TO AN OBJECT.

    slug = models.CharField(
        _("Slug"),
        max_length=255,
        help_text=_('The external identifier of the object.'),
        unique=True,
        db_index=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of item this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    description = models.CharField(
        _("Description"),
        max_length=255,
        help_text=_('The title of the object to display.'),
        blank=True,
        null=True,
    )
    member = models.OneToOneField(
        "Member",
        help_text=_('The member of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    area_coordinator = models.OneToOneField(
        "AreaCoordinator",
        help_text=_('The area coordinator of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    associate = models.OneToOneField(
        "Associate",
        help_text=_('The associate of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    staff = models.OneToOneField(
        "Staff",
        help_text=_('The staff of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    item = models.OneToOneField(
        "Item",
        help_text=_('The work-order of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    watch = models.OneToOneField(
        "Watch",
        help_text=_('The watch of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    district = models.OneToOneField(
        "District",
        help_text=_('The district of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    file = models.OneToOneField(
        "PrivateFileUpload",
        help_text=_('The file of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # THE FOLLOWING FIELDS ARE USED FOR SYSTEM PURPOSES.

    created_at = models.DateTimeField(
        _("Created At"),
        help_text=_('When the object was created.'),
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_unified_search_items",
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
    created_from_position = models.PointField(
        _("Created from position"),
        help_text=_('The latitude and longitude coordinates for the creator.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )
    last_modified_at = models.DateTimeField(
        _("Last Modified At"),
        help_text=_('When the object was last modified.'),
        blank=True,
        null=True
    )
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_unified_search_items",
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
    last_modified_from_position = models.PointField(
        _("Last modified from position"),
        help_text=_('The latitude and longitude coordinates for the last modified user.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )

    """
    FUNCTIONS
    """

    def __str__(self):
        return str(self.description)

    def save(self, *args, **kwargs):
        '''
        Override our save functionality to add the following additional
        functionality:
        '''

        # DEVELOPERS NOTE:
        # Why are we doing this? We want to handle the situation that our
        # application inputs an indexted text which is too large; therefore,
        # we will automatically truncate it so this issue will not occur.
        self.text = Truncator(self.text).chars(2047)

        '''
        Run our `save` function.
        '''
        super(UnifiedSearchItem, self).save(*args, **kwargs)

    @staticmethod
    def get_type_of_member(member):
        try:
            role_id = member.user.role_id
            if role_id == SharedGroup.GROUP_MEMBERSHIP.MEMBER:
                return UnifiedSearchItem.TYPE_OF.MEMBER
            elif role_id == SharedGroup.GROUP_MEMBERSHIP.AREA_COORDINATOR:
                return UnifiedSearchItem.TYPE_OF.AREA_COORDINATOR
            elif role_id == SharedGroup.GROUP_MEMBERSHIP.ASSOCIATE:
                return UnifiedSearchItem.TYPE_OF.ASSOCIATE
            elif role_id == SharedGroup.GROUP_MEMBERSHIP.FRONTLINE_STAFF:
                return UnifiedSearchItem.TYPE_OF.STAFF
            elif role_id == SharedGroup.GROUP_MEMBERSHIP.MANAGER:
                return UnifiedSearchItem.TYPE_OF.STAFF
            print("get_type_of_member | unsupported member role")
        except Exception as e:
            print("get_type_of_member | exception:", e)
        return -1
