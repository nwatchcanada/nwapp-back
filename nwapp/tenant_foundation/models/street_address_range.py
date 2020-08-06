# -*- coding: utf-8 -*-
import uuid
import pytz
from random import randint
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Count
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser
from shared_foundation.utils.string import get_referral_code
from shared_foundation.utils.number import get_special_range

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class StreetAddressRangeManager(models.Manager):
    def delete_all(self):
        items = StreetAddressRange.objects.all()
        for item in items.all():
            item.delete()

    def filter_missing(self, search_query, target_query):
        """
        Purpose of function is to find all the objects which are missing in the
        `target_query` that the exist in the `search_query`.
        """
        target_query_pks = target_query.values_list('pk', flat=True)
        return StreetAddressRange.objects.filter(~Q(search_query__in=target_query_pks))

    def random(self):
        """
        Function will get a single random object from the datbase.
        Special thanks via: https://stackoverflow.com/a/2118712
        """
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class StreetAddressRange(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_street_address_ranges'
        verbose_name = _('Street Address Range')
        verbose_name_plural = _('Street Address Ranges')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STREET_TYPE:
        OTHER = 1
        AVENUE = 2
        BOULEVARD = 3
        COURT = 4
        CRESCENT = 5
        DRIVE = 6
        GATE = 7
        GROVE = 8
        HILL = 9
        LANE = 10
        PLACE = 11
        ROAD = 12
        STREET = 13
        TERRACE = 14
        WAY = 15

    class STREET_DIRECTION:
        NONE = 0
        EAST = 1
        NORTH = 2
        NORTH_EAST = 3
        NORTH_WEST = 4
        SOUTH = 5
        SOUTH_EAST = 6
        SOUTH_WEST = 7
        WEST = 8

    class STREET_NUMBER_RANGE_TYPE:
        ALL = 1
        ODD = 2
        EVEN = 3

    '''
    CHOICES
    '''

    STREET_TYPE_CHOICES = (
        (STREET_TYPE.AVENUE, _('Avenue')),
        (STREET_TYPE.BOULEVARD, _('Boulevard')),
        (STREET_TYPE.COURT, _('Court')),
        (STREET_TYPE.CRESCENT, _('Crescent')),
        (STREET_TYPE.DRIVE, _('Drive')),
        (STREET_TYPE.GATE, _('Gate')),
        (STREET_TYPE.GROVE, _('Grove')),
        (STREET_TYPE.HILL, _('Hill')),
        (STREET_TYPE.LANE, _('Lane')),
        (STREET_TYPE.PLACE, _('Place')),
        (STREET_TYPE.ROAD, _('Road')),
        (STREET_TYPE.STREET, _('Street')),
        (STREET_TYPE.TERRACE, _('Terrace')),
        (STREET_TYPE.WAY, _('Way')),
        (STREET_TYPE.OTHER, _('Other')),
    )

    STREET_DIRECTION_CHOICES = (
        (STREET_DIRECTION.NONE, _('-')),
        (STREET_DIRECTION.EAST, _('East')),
        (STREET_DIRECTION.NORTH, _('North')),
        (STREET_DIRECTION.NORTH_EAST, _('North East')),
        (STREET_DIRECTION.NORTH_WEST, _('North West')),
        (STREET_DIRECTION.SOUTH, _('South')),
        (STREET_DIRECTION.SOUTH_EAST, _('South East')),
        (STREET_DIRECTION.SOUTH_WEST, _('South West')),
        (STREET_DIRECTION.WEST, _('West')),
    )

    STREET_NUMBER_RANGE_TYPE_CHOICES = (
        (STREET_NUMBER_RANGE_TYPE.ALL, _('All')),
        (STREET_NUMBER_RANGE_TYPE.ODD, _('Odd')),
        (STREET_NUMBER_RANGE_TYPE.EVEN, _('Even')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = StreetAddressRangeManager()

    '''
    MODEL FIELDS
    '''

    street_number_start = models.PositiveSmallIntegerField(
        _("Street Number Start"),
        help_text=_('Please select the street number start range.'),
    )
    street_number_end = models.PositiveSmallIntegerField(
        _("Street Number End"),
        help_text=_('Please select the street number end range.'),
    )
    street_number_range_type = models.PositiveSmallIntegerField(
        _("Street Number Range Type"),
        help_text=_('Please select the street number range type.'),
        choices=STREET_NUMBER_RANGE_TYPE_CHOICES,
        default=STREET_NUMBER_RANGE_TYPE.ALL,
        blank=True,
    )
    street_numbers = ArrayField(
        models.PositiveSmallIntegerField(),
        help_text=_('The street numbers in our range. Note: Internal implementation.'),
        blank=True,
        null=True,
    )
    street_name = models.CharField(
        _("Street Name"),
        max_length=63,
        help_text=_('The name of the street.'),
        db_index=True,
    )
    street_type = models.PositiveSmallIntegerField(
        _("Street Type"),
        help_text=_('Please select the street type.'),
        choices=STREET_TYPE_CHOICES,
    )
    street_type_other = models.CharField(
        _("Street Type (Other)"),
        max_length=127,
        help_text=_('Please select the street type not listed in our types.'),
        null=True,
        blank=True,
    )
    street_direction = models.PositiveSmallIntegerField(
        _("Street Direction"),
        help_text=_('Please select the street direction.'),
        choices=STREET_DIRECTION_CHOICES,
        blank=True,
        default=STREET_DIRECTION.NONE,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether tag was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch whom this street address range belongs to.'),
        related_name="street_address_ranges",
        on_delete=models.CASCADE,
    )

    # AUDITING FIELDS

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
        max_length=255,
        null=False,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_street_address_ranges",
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
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_street_address_ranges",
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
    MODEL FUNCTIONS
    """

    def __str__(self):
        """
        Override the default string conversion function to output a custom
        string output by the object.
        """
        actual_street_type = self.get_street_type_label()
        street_address = self.street_name + " " + actual_street_type
        if self.street_direction:
            street_address += " " + str(self.street_direction)
        street_address += " from " + str(self.street_number_start) + " to " + str(self.street_number_end)
        return street_address

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
                latest_obj = StreetAddressRange.objects.latest('id');
                self.id = latest_obj.id + 1
            except StreetAddressRange.DoesNotExist:
                self.id = 1

        '''
        If we are creating a new model, then we will automatically set `slug`.
        '''
        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            text = str(self.street_number_start)+"-to-"
            text += str(self.street_number_end)+"-"
            text += str(self.street_name)+"-"
            text += str(self.street_type)+"-"
            if self.street_type_other:
                text += str(self.street_type_other)+"-"
            text += str(self.street_direction)
            slug = slugify(text)
            while StreetAddressRange.objects.filter(slug=slug).exists():
                slug = slugify(text)+"-"+get_referral_code(16)
            self.slug = slug

        # Internal implementation of generating our street numbers.
        self.street_numbers = get_special_range(
            self.street_number_start,
            self.street_number_end,
            self.street_number_range_type
        )

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(StreetAddressRange, self).save(*args, **kwargs)

    def get_street_type_label(self):
        return self.street_type_other if self.street_type == StreetAddressRange.STREET_TYPE.OTHER else str(dict(StreetAddressRange.STREET_TYPE_CHOICES).get(self.street_type))

    def get_street_direction_label(self):
        return str(dict(StreetAddressRange.STREET_DIRECTION_CHOICES).get(self.street_direction))

    @staticmethod
    def slugs_from_data(data):
        """
        Purpose of this function is to iterate through the dictionary object
        (which generally came from an API endpoint) and extract all the primary
        keys if there is any.
        """
        slugs_arr = []
        for datum in data:
            slug = datum.get("slug", None)
            if slug:
                slugs_arr.append(slug)
        return slugs_arr

    @staticmethod
    def missing_slugs(search_slugs, target_slugs):
        """
        Utility function used to return array of slug strings for the
        objects which are missing from the `target_slugs` array of slug strings
        that did not exist in the `search_slugs` array of slug strings.
        """
        missing_slugs_arr = []
        for target_slug in target_slugs:
            if str(target_slug) not in search_slugs:
                missing_slugs_arr.append(target_slug)
        return missing_slugs_arr

    @staticmethod
    @transaction.atomic
    def seed(length=1, watch=None):
        from faker import Faker
        from tenant_foundation.models import Watch
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                # Generate our random data.
                description = faker.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
                watch = watch if watch != None else Watch.objects.random()
                street_number_start = faker.random_int(min=1, max=100, step=1)
                street_number_end = faker.random_int(min=100, max=1000, step=1)
                street_number_range_type = faker.random_int(min=1, max=3, step=1)
                street_name = faker.company()
                street_type = faker.random_int(min=2, max=6, step=1)
                street_type_other = None
                street_direction = faker.random_int(min=0, max=8, step=1)
                is_archived = False

                # Create our object.
                street_address_range = StreetAddressRange.objects.create(
                    watch=watch,
                    street_number_start = street_number_start,
                    street_number_end = street_number_end,
                    street_number_range_type = street_number_range_type,
                    street_name = street_name,
                    street_type = street_type,
                    street_type_other = street_type_other,
                    street_direction = street_direction,
                    is_archived = is_archived,
                )

                # Append to our result array.
                results.append(street_address_range)
            except Exception as e:
                print(" StreetAddressRange | seed | e:", e)
        return results
