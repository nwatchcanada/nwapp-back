import phonenumbers
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.gis.db import models
from django.db.models import Q
from django.db import transaction
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from shared_foundation.models import SharedUser


class StaffManager(models.Manager):
    def delete_all(self):
        items = Staff.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Staff.objects.filter(
            Q(user__member__indexed_text__icontains=keyword) |
            Q(user__member__indexed_text__istartswith=keyword) |
            Q(user__member__indexed_text__iendswith=keyword) |
            Q(user__member__indexed_text__exact=keyword) |
            Q(user__member__indexed_text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Staff.objects.annotate(search=SearchVector('user__member__indexed_text'),).filter(search=keyword)


class Staff(models.Model):
    """
    Class model represents the Neighbourhood Watch registered area coordinator
    for the particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_staves'
        verbose_name = _('Staff')
        verbose_name_plural = _('Staves')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class DEMOTION_REASON:
        OTHER_REASON = 1
        SOME_REASON = 2
        ANOTHER_REASON = 3

    '''
    CHOICES
    '''

    DEMOTION_REASON_CHOICES = (
        (DEMOTION_REASON.SOME_REASON, _('Some reason')),
        (DEMOTION_REASON.ANOTHER_REASON, _('Another reason')),
        (DEMOTION_REASON.OTHER_REASON, _('Other (Please specify)')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = StaffManager()

    '''
    MODEL FIELDS
    '''

    # SYSTEM FIELDS

    user = models.OneToOneField(
        SharedUser,
        help_text=_('The user whom is an staff.'),
        related_name="staff",
        on_delete=models.CASCADE,
        primary_key=True,
    )

    # BUSINESS LOGIC SPECIFIC FIELDS

    has_signed_conflict_of_interest_agreement = models.BooleanField(
        _("Has signed conflict of interest agreement"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the conflict of interest agreement.'),
        blank=True,
    )
    conflict_of_interest_agreement = models.TextField(
        _("Conflict of interest agreement"),
        help_text=_('The actual terms of conflict of interest agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    conflict_of_interest_agreement_signed_on = models.DateTimeField(
        _('Conflict of interest agreement signed on'),
        help_text=_('The date when the agreement was signed on.'),
        blank=True,
        null=True,
    )

    has_signed_code_of_conduct_agreement = models.BooleanField(
        _("Has signed code of conduct agreement"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the code of conduct.'),
        blank=True,
    )
    code_of_conduct_agreement = models.TextField(
        _("Code of conduct agreement"),
        help_text=_('The code of conduct agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    code_of_conduct_agreement_signed_on = models.DateTimeField(
        _('Code of conduct agreement signed on'),
        help_text=_('The date when the code of conduct agreement was signed on.'),
        blank=True,
        null=True,
    )

    has_signed_confidentiality_agreement = models.BooleanField(
        _("Has signed confidentiality agreement"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the confidentiality agreement.'),
        blank=True,
    )
    confidentiality_agreement = models.TextField(
        _("Confidentiality agreement agreement"),
        help_text=_('The actual terms of confidentiality agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    confidentiality_agreement_signed_on = models.DateTimeField(
        _('Confidentiality agreement signed on'),
        help_text=_('The date when the agreement was signed on.'),
        blank=True,
        null=True,
    )

    has_signed_staff_agreement = models.BooleanField(
        _("Has signed staff agreement"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the staff agreement.'),
        blank=True,
    )
    staff_agreement = models.TextField(
        _("Staff agreement"),
        help_text=_('The actual terms of staff agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    staff_agreement_signed_on = models.DateTimeField(
        _('Staff agreement signed on'),
        help_text=_('The date when the staff agreement was signed on.'),
        blank=True,
        null=True,
    )

    police_check_date = models.DateField(
        _('Police check date'),
        help_text=_('The date when the police check was taken on.'),
        blank=True,
        null=True,
    )
    demotion_reason = models.PositiveSmallIntegerField(
        _("Demotion Reason"),
        help_text=_('The reason for the demotion.'),
        choices=DEMOTION_REASON_CHOICES,
        null=True,
        blank=True,
    )
    demotion_reason_other = models.TextField(
        _("Demotion Reason (Other)"),
        help_text=_('The other reason for the demotion.'),
        blank=True,
        null=True,
    )

    # AUDITING FIELDS

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_staves",
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
        related_name="last_modified_staves",
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
        return self.user.get_full_name()

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Staff, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.user.get_full_name()

    def get_pretty_state(self):
        return str(dict(Staff.STATE_CHOICES).get(self.user.member.state))

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
