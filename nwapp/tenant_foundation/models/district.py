# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class DistrictManager(models.Manager):
    def delete_all(self):
        items = District.objects.all()
        for item in items.all():
            item.delete()


class District(models.Model):
    """
    Class represents the growing medium that the crop can live in.
    """

    '''
    Constants & Choices
    '''

    class TYPE_OF:
        PLANT = 1
        FISHSTOCK = 2
        ANIMALSTOCK = 3
        NONE = 0

    TYPE_OF_CHOICES = (
        (TYPE_OF.PLANT, _('Plant')),
        (TYPE_OF.FISHSTOCK, _('Fishstock')),
        (TYPE_OF.ANIMALSTOCK, _('Animalstock')),
        (TYPE_OF.NONE, _('None')),
    )

    '''
    Metadata
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_districts'
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    # Variable used to keep track of the original value.
    __original_name = None

    '''
    Object Manager
    '''

    objects = DistrictManager()
    tenant = models.ForeignKey(
        "shared_foundation.SharedOrganization",
        help_text=_('The tenant this district belongs to.'),
        related_name="districts",
        on_delete=models.CASCADE
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this district when accessing the details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name of the district.'),
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )

    '''
    Methods.
    '''

    def __init__(self, *args, **kwargs):
        """
        Override the initializer to support storing the `name` which we will
        use to detect changes in the name.
        """
        super(District, self).__init__(*args, **kwargs)
        self.__original_name = self.name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on tenant's location.
        (b) Else generate slug with random string attached.
        (2) If the name was changed then we need to update the slug.
        """
        if not self.slug or self.name != self.__original_name:
            # Generate our slug.
            slug = slugify(self.tenant.country)+"-"
            slug += slugify(self.tenant.region)+"-"
            slug += slugify(self.tenant.locality)+"-"
            slug += slugify(self.name)
            self.slug = slug

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while District.objects.filter(slug=self.slug).exists():
                self.slug = self.slug+"-"+get_random_string(length=8)

        super(District, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_name = self.name

    def __str__(self):
        return str(self.name)
