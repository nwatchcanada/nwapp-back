# -*- coding: utf-8 -*-
import pytz
import uuid
from random import randint
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import transaction
from django.db.models.aggregates import Count
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedUser, e164_phone_regex
from shared_foundation.utils.string import get_referral_code


class DistrictManager(models.Manager):
    def delete_all(self):
        items = District.objects.all()
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return District.objects.filter(
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )

    def random(self):
        """
        Function will get a single random object from the datbase.
        Special thanks via: https://stackoverflow.com/a/2118712
        """
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class District(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_districts'
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        # ordering = ['-created_at']
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class TYPE_OF:
        RESIDENTIAL = 1
        BUSINESS = 2
        COMMUNITY_CARES = 3

    '''
    CHOICES
    '''

    TYPE_OF_CHOICES = (
        (TYPE_OF.RESIDENTIAL, _('Residential')),
        (TYPE_OF.BUSINESS, _('Business')),
        (TYPE_OF.COMMUNITY_CARES, _('Community Cares')),
    )

    TYPE_OF_CODE_CHOICES = (
        (TYPE_OF.RESIDENTIAL, 'rez'),
        (TYPE_OF.BUSINESS, 'biz'),
        (TYPE_OF.COMMUNITY_CARES, 'com'),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = DistrictManager()

    '''
    MODEL FIELDS
    '''

    #  COMMON FIELDS

    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of score point this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=127,
        help_text=_('The name of this district.'),
        unique=True,
        db_index=True,
    )
    description = models.CharField(
        _("Description"),
        help_text=_('The description of this district.'),
        max_length=255,
        null=True,
        blank=True,
    )
    governors = models.ManyToManyField(
        "Associate",
        help_text=_('The associates which are responsible for the operation of the district.'),
        blank=True,
        related_name="governing"
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this district.'),
        blank=True,
        related_name="districts"
    )
    boundry_position = models.PointField(
        _("Boundry Position"),
        help_text=_('The centre coordinates to apply for every map rendered on the user\'s screen.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )
    boundry_zoom = models.FloatField(
        _("Boundry Map Zoom"),
        help_text=_('The centre zoom to apply for every map rendered on the user\'s screen.'),
        null=True,
        blank=True,
    )
    boundry_polygon = models.PolygonField(
        _("Boundry Polygon"),
        help_text=_('The polygon of the district\'s boundry.'),
        blank=True,
        null=True,
        spatial_index=True,
    )

    # RESIDENTIAL FIELDS

    counselor_name = models.CharField(
        _("Counselor Name"),
        help_text=_('The name of this district\'s counselor.'),
        max_length=127,
        null=True,
        blank=True,
    )
    counselor_email = models.EmailField(
        _("Counselor Email"),
        help_text=_('The email of this district\'s counselor.'),
        max_length=127,
        null=True,
        blank=True,
    )
    counselor_phone = models.CharField(
        _("Counselor Phone"),
        help_text=_('The phone of this district\'s counselor.'),
        max_length=31,
        validators=[e164_phone_regex],
        null=True,
        blank=True,
    )

    # BUSINESS FIELDS

    website_url = models.URLField(
        _("Website URL"),
        help_text=_('The external website link of this district.'),
        max_length=255,
        null=True,
        blank=True,
    )
    logo_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The logo image of this district.'),
        related_name="districts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

    # SYSTEM FIELDS

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
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether district was archived or not'),
        default=False,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this score point.'),
        related_name="created_districts",
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
        related_name="last_modified_districts",
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
        return str(self.slug)

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
                latest_obj = District.objects.latest('id');
                self.id = latest_obj.id + 1
            except District.DoesNotExist:
                self.id = 1

        # Assign our unique slug to this model as our external identifier.
        if self.slug == None or self.slug == "":
            # The following code will generate a unique slug and if the slug
            # is not unique in the database, then continue to try generating
            # a unique slug until it is found.
            slug = slugify(self.name)
            while District.objects.filter(slug=slug).exists():
                slug = slugify(self.name)+"-"+get_referral_code(4)
            self.slug = slug

        # Update our searchable content.
        text = str(self.name) + " " + str(self.description)
        if self.counselor_name:
            text += str(self.counselor_name)
        if self.counselor_email:
            text += " " + str(self.counselor_email)
        if self.counselor_phone:
            text += " " + str(self.counselor_phone)
        if self.website_url:
            text += " " + str(self.website_url)
        if self.type_of:
            text += " " + self.get_type_of_label()
        if self.slug:
            text += " " + str(self.slug)
        self.indexed_text = text

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(District, self).save(*args, **kwargs)

    def get_type_of_label(self):
        return str(dict(District.TYPE_OF_CHOICES).get(self.type_of))

    def get_type_of_code(self):
        return str(dict(District.TYPE_OF_CODE_CHOICES).get(self.type_of))

    @staticmethod
    def seed(length):
        from faker import Faker
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                type_of = faker.random_int(min=1, max=3, step=1)
                name = faker.company() + " District"
                description = faker.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
                counselor_name = faker.name()
                counselor_email = faker.email()
                counselor_phone = faker.phone_number()
                website_url = faker.uri()
                # print(
                #     type_of, "\n", name, "\n", description, "\n",
                #     counselor_name, "\n", counselor_email, "\n", counselor_phone, "\n",
                #     website_url, "\n",
                # )
                district = District.objects.create(
                    type_of=type_of,
                    name=name,
                    description=description,
                    counselor_name=counselor_name,
                    counselor_email=counselor_email,
                    counselor_phone=counselor_phone,
                    website_url=website_url,
                )
                results.append(district)
            except Exception as e:
                print(e)
                pass
        return results
