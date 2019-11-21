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


class MemberManager(models.Manager):
    def delete_all(self):
        items = Member.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Member.objects.filter(
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
        return Member.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


class Member(models.Model):
    """
    Class model represents the Neighbourhood Watch registered member for the
    particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_members'
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class MEMBER_STATE:
        ACTIVE = 'active'
        INACTIVE = 'inactive'

    class MEMBER_TYPE_OF:
        BUSINESS = 'business'
        RESIDENTIAL = 'residential'
        COMMUNITY_CARES = 'community_cares'

    class MEMBER_DEACTIVATION_REASON:
        NOT_SPECIFIED = 0
        OTHER = 1
        BLACKLISTED = 2
        MOVED = 3
        DECEASED = 4
        DO_NOT_CONTACT = 5

    class MEMBER_ORGANIZATION_TYPE_OF:
        PRIVATE = 'private'
        GOVERNMENT = 'government'
        NON_PROFIT = 'non_profit'
        UNSPECIFIED = 'unspecified'

    '''
    CHOICES
    '''

    MEMBER_STATE_CHOICES = (
        (MEMBER_STATE.ACTIVE, _('Active')),
        (MEMBER_STATE.INACTIVE, _('Inactive')),
    )

    MEMBER_TYPE_OF_CHOICES = (
        (MEMBER_TYPE_OF.BUSINESS, _('Business')),
        (MEMBER_TYPE_OF.RESIDENTIAL, _('Residential')),
        (MEMBER_TYPE_OF.COMMUNITY_CARES, _('Community Cares')),
    )

    MEMBER_DEACTIVATION_REASON_CHOICES = (
        (MEMBER_DEACTIVATION_REASON.BLACKLISTED, _('Blacklisted')),
        (MEMBER_DEACTIVATION_REASON.MOVED, _('Moved')),
        (MEMBER_DEACTIVATION_REASON.DECEASED, _('Deceased')),
        (MEMBER_DEACTIVATION_REASON.DO_NOT_CONTACT, _('Do not contact')),
        (MEMBER_DEACTIVATION_REASON.NOT_SPECIFIED, _('Not specified')),
        (MEMBER_DEACTIVATION_REASON.OTHER, _('Other')),
    )

    MEMBER_ORGANIZATION_TYPE_OF_CHOICES = (
        (MEMBER_ORGANIZATION_TYPE_OF.PRIVATE, _('Private')),
        (MEMBER_ORGANIZATION_TYPE_OF.GOVERNMENT, _('Government')),
        (MEMBER_ORGANIZATION_TYPE_OF.NON_PROFIT, _('Non-Profit')),
        (MEMBER_ORGANIZATION_TYPE_OF.UNSPECIFIED, _('Unspecified')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = MemberManager()

    '''
    MODEL FIELDS
    '''

    # SYSTEM FIELDS

    user = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom owns this thing.'),
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_abstract_thing_owner_related",
        on_delete=models.CASCADE
    )
    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=511,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of member this is.'),
        choices=MEMBER_TYPE_OF_CHOICES,
        db_index=True,
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

    # PERSONAL & CONTACT FIELDS

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

    # ORGANIZATION FIELDS

    organization_name = models.CharField(
        _("Organization Name"),
        max_length=255,
        help_text=_('The name of the organization or business this person represents.'),
        blank=True,
        null=True,
    )
    organization_type_of = models.PositiveSmallIntegerField(
        _("Organization Type of"),
        help_text=_('The type of organization this is based on Neighbourhood Watch Canada internal classification.'),
        default=MEMBER_ORGANIZATION_TYPE_OF.UNSPECIFIED,
        blank=True,
        choices=MEMBER_ORGANIZATION_TYPE_OF_CHOICES,
    )

    # WATCH
    #TODO: IMPLEMENT

    # STATE FIELDS

    state = models.CharField(
        _('State'),
        help_text=_('The state of this member.'),
        max_length=15,
        choices=MEMBER_STATE_CHOICES,
        default=MEMBER_STATE.ACTIVE,
        blank=True,
        db_index=True,
    )
    deactivation_reason = models.PositiveSmallIntegerField(
        _("Deactivation reason"),
        help_text=_('The reason why this member was deactivated.'),
        blank=True,
        choices=MEMBER_DEACTIVATION_REASON_CHOICES,
        default=MEMBER_DEACTIVATION_REASON.NOT_SPECIFIED
    )
    deactivation_reason_other = models.CharField(
        _("Deactivation reason (other)"),
        max_length=2055,
        help_text=_('The reason why this member was deactivated which was not in the list.'),
        blank=True,
        default=""
    )

    # AUDITING FIELDS

    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_members",
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
        related_name="last_modified_members",
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
            self.id = Member.objects.count() + 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Member, self).save(*args, **kwargs)

    def get_pretty_state(self):
        return dict(MEMBER_STATE_CHOICES).get(self.state)

    def get_pretty_type_of(self):
        return dict(MEMBER_TYPE_OF_CHOICES).get(self.type_of)

    def get_pretty_deactivation_reason(self):
        return dict(MEMBER_DEACTIVATION_REASON_CHOICES).get(self.deactivation_reason)

    def get_pretty_organization_type_of(self):
        return dict(MEMBER_ORGANIZATION_TYPE_OF_CHOICES).get(self.organization_type_of)

    @cached_property
    def fullname(self):
        return self.first_name + " " + self.last_name


    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'fullname':
                del self.fullname
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def invalidate_all(self):
        self.invalidate("fullname")
