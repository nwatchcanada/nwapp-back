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


class MemberContactManager(models.Manager):
    def delete_all(self):
        items = MemberContact.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return MemberContact.objects.filter(
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return MemberContact.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


class MemberContact(models.Model):
    """
    Class model represents the Neighbourhood Watch registered member for the
    particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_member_contacts'
        verbose_name = _('Member Contact')
        verbose_name_plural = _('Member Contacts')
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

    objects = MemberContactManager()

    '''
    MODEL FIELDS
    '''

    # SYSTEM FIELDS

    member = models.OneToOneField(
        "Member",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether member allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether member allows being reached by text.'),
        default=True,
        blank=True
    )
    first_name = models.CharField(
        _("First Name"),
        max_length=63,
        help_text=_('The member\'s given name.'),
        blank=True,
        null=True,
        db_index=False,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The member\'s sure name.'),
        blank=True,
        null=True,
        db_index=False,
    )
    email = models.EmailField(
        _("Email"),
        help_text=_('Email address.'),
        null=True,
        blank=True,
        validators=[email_validator],
        db_index=True
    )
    primary_phone = PhoneNumberField(
        _("Primary Telephone"),
        help_text=_('The primary telephone number used by the member.'),
        blank=True,
        null=True,
    )
    secondary_phone = PhoneNumberField(
        _("Secondary Telephone"),
        help_text=_('The secondary or other telephone number used by the member.'),
        blank=True,
        null=True,
    )

    # AUDITING FIELDS

    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_member_contacts",
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
        related_name="last_modified_member_contacts",
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
            self.id = MemberContact.objects.count() + 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(MemberContact, self).save(*args, **kwargs)
