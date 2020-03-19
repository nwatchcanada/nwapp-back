# -*- coding: utf-8 -*-
import csv
import pytz
from random import randint
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Count
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser
from shared_foundation.utils.string import get_referral_code

# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class WatchManager(models.Manager):
    def delete_all(self):
        items = Watch.objects.all()
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Watch.objects.filter(
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )

    def search_nearby_address(self, street_number, street_name, street_type, street_type_other):
        from psycopg2.extras import NumericRange
        from tenant_foundation.models import StreetAddressRange

        # Special thanks via
        # https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/fields/#containment-functions
        addresses = StreetAddressRange.objects.filter(
            Q(street_numbers__contains=NumericRange(street_number, street_number))
            &Q(street_name=street_name)
            &Q(is_archived=False)
        )

        if street_type == StreetAddressRange.STREET_TYPE.OTHER:
            addresses = addresses.filter(street_type_other = street_type_other)
        else:
            addresses = addresses.filter(street_type = street_type)

        # print("RANGES", addresses)
        return Watch.objects.filter(street_address_ranges__in=addresses).order_by('name')

    def random(self):
        """
        Function will get a single random object from the datbase.
        Special thanks via: https://stackoverflow.com/a/2118712
        """
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Watch(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_watches'
        verbose_name = _('Watch')
        verbose_name_plural = _('Watches')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STATE:
        ACTIVE = 'active'
        INACTIVE = 'inactive'

    class TYPE_OF:
        RESIDENTIAL = 1
        BUSINESS = 2
        COMMUNITY_CARES = 3

    class DEACTIVATION_REASON:
        NOT_SPECIFIED = 0
        OTHER = 1
        NO_AREA_COORDINATOR = 2
        OPTED_OUT = 3
        NOT_COMPLIANT = 4

    '''
    CHOICES
    '''

    STATE_CHOICES = (
        (STATE.ACTIVE, _('Active')),
        (STATE.INACTIVE, _('Inactive')),
    )

    TYPE_OF_CHOICES = (
        (TYPE_OF.BUSINESS, _('Business')),
        (TYPE_OF.RESIDENTIAL, _('Residential')),
        (TYPE_OF.COMMUNITY_CARES, _('Community Cares')),
    )

    DEACTIVATION_REASON_CHOICES = (
        (DEACTIVATION_REASON.NO_AREA_COORDINATOR, _('No Area Coordinator')),
        (DEACTIVATION_REASON.OPTED_OUT, _('Watch has collectively opted out of program')),
        (DEACTIVATION_REASON.NOT_COMPLIANT, _('Watch Area not compliant')),
        (DEACTIVATION_REASON.OTHER, _('Other')),
        (DEACTIVATION_REASON.NOT_SPECIFIED, _('Not specified')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = WatchManager()

    '''
    MODEL FIELDS
    '''

    state = models.CharField(
        _('State'),
        help_text=_('The state of this watch.'),
        max_length=15,
        choices=STATE_CHOICES,
        default=STATE.ACTIVE,
        blank=True,
        db_index=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of watch this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name of this watch.'),
        db_index=True,
        unique=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this watch.'),
        blank=True,
        null=True,
        default='',
    )
    district = models.ForeignKey(
        "District",
        help_text=_('The district whom this watch belongs to.'),
        related_name="watches",
        on_delete=models.CASCADE,
    )
    is_virtual = models.BooleanField(
        _("Is Virtual Watch"),
        help_text=_('Indicates whether watch is a virtual watch.'),
        default=False,
        blank=True,
        db_index=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this watch.'),
        blank=True,
        related_name="watches"
    )
    deactivation_reason = models.PositiveSmallIntegerField(
        _("Deactivation reason"),
        help_text=_('The reason why this watch was deactivated.'),
        blank=True,
        choices=DEACTIVATION_REASON_CHOICES,
        default=DEACTIVATION_REASON.NOT_SPECIFIED
    )
    deactivation_reason_other = models.CharField(
        _("Deactivation reason (other)"),
        max_length=2055,
        help_text=_('The reason why this watch was deactivated which was not in the list.'),
        blank=True,
        null=True,
        default=""
    )

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
        related_name="created_watches",
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
        related_name="last_modified_watches",
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
        return str(self.name)

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
                latest_obj = Watch.objects.latest('id');
                self.id = latest_obj.id + 1
            except Watch.DoesNotExist:
                self.id = 1

        '''
        If we are creating a new model, then we will automatically create `slug`.
        '''
        # The following code will generate a unique slug and if the slug
        # is not unique in the database, then continue to try generating
        # a unique slug until it is found.
        if self.slug == "" or self.slug == None:
            slug = slugify(self.name)
            while Watch.objects.filter(slug=slug).exists():
                slug = slugify(self.name)+"-"+get_referral_code(16)
            self.slug = slug

        # The following code will create the searchable content.
        # tags slug
        self.indexed_text = str(self.name) + " " + str(self.description) + " " + str(self.district.indexed_text)
        if self.pk != None:
            tag_names = self.tags.values_list('text', flat=True)
            for tag_name in tag_names:
                self.indexed_text += str(tag_name) + ", "

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Watch, self).save(*args, **kwargs)

    def get_state_label(self):
        return str(dict(Watch.STATE_CHOICES).get(self.state))

    def get_type_of_label(self):
        return str(dict(Watch.TYPE_OF_CHOICES).get(self.type_of))

    def get_deactivation_reason_label(self):
        return str(dict(Watch.DEACTIVATION_REASON_CHOICES).get(self.deactivation_reason))

    def get_searchable_content(self):
        return self.indexed_text

    @staticmethod
    def seed(length):
        from faker import Faker
        from tenant_foundation.models import District
        from tenant_foundation.models import StreetAddressRange
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                # Generate our random data.
                name = faker.company() + " Watch"
                description = faker.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
                district = District.objects.random()
                street_address_ranges_count = faker.random_int(min=1, max=100, step=1)

                # Generate the watch.
                watch = Watch.objects.create(
                    type_of=district.type_of,
                    name=name,
                    description=description,
                    district=district,
                )

                # Generate the street address ranges.
                StreetAddressRange.seed(street_address_ranges_count, watch)

                # Append to our result array.
                results.append(watch)
            except Exception as e:
                print(e)
        return results
