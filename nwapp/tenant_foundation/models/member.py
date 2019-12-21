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

from shared_foundation.models import SharedUser

# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


class MemberManager(models.Manager):
    def delete_all(self):
        items = Member.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()

    def default_search(self, keyword):
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
        RESIDENTIAL = 1
        BUSINESS = 2
        COMMUNITY_CARES = 3

    class MEMBER_DEACTIVATION_REASON:
        NOT_SPECIFIED = 0
        OTHER = 1
        BLACKLISTED = 2
        MOVED = 3
        DECEASED = 4
        DO_NOT_CONTACT = 5

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

    '''
    OBJECT MANAGERS
    '''

    objects = MemberManager()

    '''
    MODEL FIELDS
    '''

    # SYSTEM FIELDS

    user = models.OneToOneField(
        SharedUser,
        help_text=_('The user whom is a member.'),
        related_name="member",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of member this is.'),
        choices=MEMBER_TYPE_OF_CHOICES,
        db_index=True,
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
        null=True,
        default=""
    )

    # AUDITING FIELDS

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
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
    last_modified_at = models.DateTimeField(auto_now=True)
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

    """
    MODEL FUNCTIONS
    """

    def __str__(self):
        '''
        Override the `casting` function so we output the following string when
        an object gets casted to a string.
        '''
        return str(self.user)

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Member, self).save(*args, **kwargs)

    def get_pretty_state(self):
        return str(dict(Member.MEMBER_STATE_CHOICES).get(self.state))

    def get_pretty_type_of(self):
        return str(dict(Member.MEMBER_TYPE_OF_CHOICES).get(self.type_of))

    def get_pretty_deactivation_reason(self):
        return str(dict(Member.MEMBER_DEACTIVATION_REASON_CHOICES).get(self.deactivation_reason))

    def invalidate(self, method_name): #TODO: IMPLEMENT
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            pass
            # if method_name == 'fullname':
            #     del self.fullname
            # else:
            #     raise Exception("Method name not found.")
        except AttributeError:
            pass

    def invalidate_all(self):
        self.invalidate("fullname")
