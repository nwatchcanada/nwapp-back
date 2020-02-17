from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Q
from django.db import transaction
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from shared_foundation.models import SharedUser

# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


class MemberAddressManager(models.Manager):
    def delete_all(self):
        items = MemberAddress.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()


class MemberAddress(models.Model):
    """
    Class model represents the Neighbourhood Watch registered member for the
    particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_member_addresses'
        verbose_name = _('Member Address')
        verbose_name_plural = _('Member Addresses')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STREET_TYPE:
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
    CHOICES
    '''

    STREET_TYPE_CHOICES = (
        (STREET_TYPE.AVENUE, _('Avenue')),
        (STREET_TYPE.DRIVE, _('Drive')),
        (STREET_TYPE.ROAD, _('Road')),
        (STREET_TYPE.STREET, _('Street')),
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

    '''
    OBJECT MANAGERS
    '''

    objects = MemberAddressManager()

    '''
    MODEL FIELDS
    '''

    member = models.OneToOneField(
        "Member",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="address"
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

    # AUDITING FIELDS

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_member_addresses",
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
        related_name="last_modified_member_addresses",
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
        '''
        Override the `casting` function so we output the following string when
        an object gets casted to a string.
        '''
        return str(self.member)

    def get_searchable_content(self):
        """
        Function returns text data of this object we can use for searching purposes.
        """
        text = ""
        text += " " + self.postal_address
        text += " " + self.google_maps_url
        return text

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
            latest_obj = MemberAddress.objects.latest('id');
            self.id = 1 if latest_obj == None else latest_obj.id + 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(MemberAddress, self).save(*args, **kwargs)

    def get_pretty_street_type(self):
        return str(dict(MemberAddress.STREET_TYPE_CHOICES).get(self.street_type))

    def get_pretty_street_direction(self):
        return str(dict(MemberAddress.STREET_DIRECTION_CHOICES).get(self.street_direction))

    @cached_property
    def country_code(self):
        if self.country == "Canada":
            return "CA"
        else:
            print("country_code - COUNTRY NOT SPECIFIED")
            return "CA" #TODO: Pay off technical debit by finding out how to handle other countries.

    @cached_property
    def street_address(self):
        address = ""
        if self.apartment_unit:
            address = str(self.apartment_unit) + "-"
        address += str(self.street_number) + " "
        address += str(self.street_name) + " "
        if self.street_type == MemberAddress.STREET_TYPE.OTHER:
            address += self.street_type_other
        else:
            address += self.get_pretty_street_type()
        if self.street_direction != MemberAddress.STREET_DIRECTION.NONE:
            address += " " + self.get_pretty_street_direction()
        return address

    @cached_property
    def postal_address_without_postal_code(self):
        address = ""
        address += str(self.street_address)
        address += ', ' + str(self.city)
        address += ', ' + str(self.province)
        address += ', ' + str(self.country)
        return str(address)

    @cached_property
    def postal_address(self):
        the_address = self.postal_address_without_postal_code
        the_address += ', ' + self.postal_code.upper()
        return the_address

    @cached_property
    def google_maps_url(self):
        return "https://www.google.com/maps/place/%(postal_address)s" % {
            'postal_address': self.postal_address
        }

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'fullname':
                del self.fullname
            if method_name == 'country_code':
                del self.country_code
            if method_name == 'street_address':
                del self.street_address
            if method_name == 'postal_address_without_postal_code':
                del self.postal_address_without_postal_code
            if method_name == 'postal_address':
                del self.postal_address
            if method_name == 'google_maps_url':
                del self.google_maps_url
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def invalidate_all(self):
        self.invalidate("fullname")
        self.invalidate("country_code")
        self.invalidate("street_address")
        self.invalidate("postal_address_without_postal_code")
        self.invalidate("postal_address")
        self.invalidate("google_maps_url")
