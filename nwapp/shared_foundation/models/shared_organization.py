# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import BrinIndex
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django_tenants.models import TenantMixin, DomainMixin

from shared_foundation.constants import TIMEZONE_CHOICES


class SharedOrganizationManager(models.Manager):
    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return SharedOrganization.objects.annotate(
            search=SearchVector('name', 'description',),
        ).filter(search=keyword)

    def delete_all(self):
        for obj in SharedOrganization.objects.iterator(chunk_size=500):
            obj.delete()


def validate_schema(value):
    if any(c.isupper() for c in value):
        raise ValidationError(
            _('%(value)s cannot contain any uppercase characters in schema, it must all be lowercase characters.'),
            params={'value': value},
        )


class SharedOrganization(TenantMixin):
    """
    Class model to represent our tenant that all other data will be attached to.
    """

    '''
    Metadata
    '''

    class Meta:
        app_label = 'shared_foundation'
        db_table = 'nwapp_shared_organizations'
        verbose_name = _('Shared Organization')
        verbose_name_plural = _('Shared Organizations')
        default_permissions = ()
        permissions = ()
        indexes = (
            BrinIndex(
                fields=['created_at', 'last_modified_at',],
                autosummarize=True,
            ),
        )

    '''
    Constants
    '''

    class STREET_TYPE:
        UNSPECIFIED = 0
        OTHER = 1
        AVENUE = 2
        DRIVE = 3
        ROAD = 4
        STREET = 5
        WAY = 6

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

    '''
    Choices
    '''

    STREET_TYPE_CHOICES = (
        (STREET_TYPE.UNSPECIFIED, _('-')),
        (STREET_TYPE.AVENUE, _('Avenue')),
        (STREET_TYPE.DRIVE, _('Drive')),
        (STREET_TYPE.ROAD, _('Road')),
        (STREET_TYPE.STREET, _('Street')),
        (STREET_TYPE.WAY, _('Way')),
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

    '''
    Object Managers
    '''

    objects = SharedOrganizationManager()

    '''
    Fields
    '''

    #
    #  FIELDS
    #

    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name this organization.'),
    )
    alternate_name = models.CharField(
        _("Alternate Name"),
        max_length=63,
        help_text=_('The alternate name this organization.'),
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this organization.'),
    )
    country = models.CharField(
        _("Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
    )
    province = models.CharField(
        _("Province"),
        max_length=127,
        help_text=_('The province. For example, CA.'),
    )
    city = models.CharField(
        _("City"),
        max_length=127,
        help_text=_('The city. For example, Mountain View.'),
    )
    street_number = models.CharField(
        _("Street Number"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    street_name = models.CharField(
        _("Street Name"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    apartment_unit = models.CharField(
        _("Apartment Unit"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    street_type = models.PositiveSmallIntegerField(
        _("Street Type"),
        help_text=_('Please select the street type.'),
        choices=STREET_TYPE_CHOICES,
        blank=True,
        default=STREET_TYPE.UNSPECIFIED,
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
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=32,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    timezone_name = models.CharField(
        _("Timezone Name"),
        help_text=_('The timezone that this organization belongs to.'),
        max_length=32,
        choices=TIMEZONE_CHOICES,
        default="UTC"
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        'SharedUser',
        help_text=_('The user whom created this organization.'),
        related_name="created_shared_organizations",
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
        'SharedUser',
        help_text=_('The user whom last modified this organization.'),
        related_name="last_modified_shared_organizations",
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

    '''
    Methods
    '''

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.
        """
        # If no `id` was set then we'll set it ourselves.
        if self.id is None:
            self.id = SharedOrganization.objects.count() + 1
        super(SharedOrganization, self).save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return str(self.schema_name)

    def get_absolute_url(self):
        return "/shared-organization/"+str(self.schema_name)

    @cached_property
    def is_public(self):
        return self.schema_name == "public"

    @cached_property
    def country_code(self):
        if self.country == "Canada":
            return "CA"

        #TODO: Pay off technical debit by finding out how to handle other countries.
        else:
            return "CA"

    def get_pretty_street_type(self):
        return str(dict(SharedOrganization.STREET_TYPE_CHOICES).get(self.street_type))

    def get_pretty_street_direction(self):
        return str(dict(SharedOrganization.STREET_DIRECTION_CHOICES).get(self.street_direction))


class SharedOrganizationDomain(DomainMixin):
    class Meta:
        app_label = 'shared_foundation'
        db_table = 'nwapp_organization_domains'
        verbose_name = _('Shared Domain')
        verbose_name_plural = _('Shared Domains')

    pass
