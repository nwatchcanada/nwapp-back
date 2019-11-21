import phonenumbers
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Q
from django.db import transaction
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from phonenumber_field.modelfields import PhoneNumberField

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

    '''
    CHOICES
    '''

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
    street_type = models.CharField(
        _("Region"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    street_type_other = models.CharField(
        _("Street Type Other"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    street_direction = models.CharField(
        _("Street Direction"),
        max_length=127,
        help_text=_('-'),
        null=True,
        blank=True,
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=32,
        help_text=_('-'),
        null=True,
        blank=True,
    )

    # AUDITING FIELDS

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
        return str(self.first_name)+" "+str(self.last_name)


    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        # '''
        # The following code will populate our indexed_custom search text with
        # the latest model data before we save.
        # '''
        # search_text = str(self.id)
        # search_text += " " + intcomma(self.id)
        # if self.last_name:
        #     search_text += " " + self.last_name
        # if self.first_name:
        #     search_text += " " + self.first_name
        # if self.organization_name:
        #     search_text += " " + self.organization_name
        # search_text += " " + str(self.id)
        # if self.email:
        #     search_text += " " + self.email
        # if self.primary_phone:
        #     search_text += " " + phonenumbers.format_number(self.primary_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
        #     search_text += " " + phonenumbers.format_number(self.primary_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        #     search_text += " " + phonenumbers.format_number(self.primary_phone, phonenumbers.PhoneNumberFormat.E164)
        # if self.secondary_phone:
        #     search_text += " " + phonenumbers.format_number(self.secondary_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
        #     search_text += " " + phonenumbers.format_number(self.secondary_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        #     search_text += " " + phonenumbers.format_number(self.secondary_phone, phonenumbers.PhoneNumberFormat.E164)
        # # if self.description:
        # #     search_text += " " + self.description
        # self.indexed_text = Truncator(search_text).chars(511)

        '''
        If we are creating a new model, then we will automatically increment the `id`.
        '''
        if self.id == 0 or self.id == None:
            self.id = MemberAddress.objects.count() + 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(MemberAddress, self).save(*args, **kwargs)

    @cached_property
    def street_address(self):
        address = ""
        return None

    @cached_property
    def postal_address_without_postal_code(self):
        address = ""
        address += self.street_address
        address += ', ' + self.address_locality
        address += ', ' + self.address_region
        address += ', ' + self.address_country
        return address

    @cached_property
    def postal_address(self):
        address = self.postal_address_without_postal_code()
        address += ', ' + self.postal_code.upper()
        return address

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
        self.invalidate("street_address")
        self.invalidate("postal_address_without_postal_code")
        self.invalidate("postal_address")
        self.invalidate("google_maps_url")
