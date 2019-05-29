# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import BrinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


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


def validate_subdomain(value):
    if any(c.isupper() for c in value):
        raise ValidationError(
            _('%(value)s cannot contain any uppercase characters in subdomain, it must all be lowercase characters.'),
            params={'value': value},
        )


class SharedOrganization(models.Model):
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
    Constants & Choices
    '''

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

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    subdomain = models.CharField(
        _("subdomain"),
        max_length=255,
        help_text=_('The subdomain name used for this organization.'),
        db_index=True,
        unique=True,
        validators=[validate_subdomain]
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name this organization.'),
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
    region = models.CharField(
        _("Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
    )
    locality = models.CharField(
        _("Locality"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
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

    def __str__(self):
        return str(self.subdomain)

    def get_absolute_url(self):
        return "/shared-organization/"+str(self.subdomain)

    def get_pretty_type_of(self):
        return "Production Inspection"
