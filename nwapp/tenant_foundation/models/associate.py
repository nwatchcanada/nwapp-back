import phonenumbers
import uuid
from random import randint
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.gis.db import models
from django.db.models import Q
from django.db import transaction
from django.utils.text import Truncator
from django.db.models.aggregates import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from shared_foundation.models import SharedUser, SharedGroup


class AssociateManager(models.Manager):
    def delete_all(self):
        items = Associate.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Associate.objects.filter(
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
        return Associate.objects.annotate(search=SearchVector('user__member__indexed_text'),).filter(search=keyword)

    def random(self):
        """
        Function will get a single random object from the datbase.
        Special thanks via: https://stackoverflow.com/a/2118712
        """
        count = self.filter(
            user__groups__id=SharedGroup.GROUP_MEMBERSHIP.ASSOCIATE
        ).aggregate(
            count=Count('user_id')
        )['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Associate(models.Model):
    """
    Class model represents the Neighbourhood Watch registered area coordinator
    for the particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_associates'
        verbose_name = _('Associate')
        verbose_name_plural = _('Associates')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class STATE:
        ACTIVE = 'active'
        INACTIVE = 'inactive'

    class DEMOTION_REASON:
        OTHER_REASON = 1
        RETIRED_REASON = 2
        HEALTH_REASON = 3
        NO_LONGER_WANTS_ROLE_REASON = 4
        REPRIMAND_REASON = 5

    class TYPE_OF:
        RESIDENTIAL = 1
        BUSINESS = 2
        COMMUNITY_CARES = 3

    '''
    CHOICES
    '''

    STATE_CHOICES = (
        (STATE.ACTIVE, _('Active')),
        (STATE.INACTIVE, _('Inactive')),
    )

    DEMOTION_REASON_CHOICES = (
        (DEMOTION_REASON.RETIRED_REASON, _('Retired')),
        (DEMOTION_REASON.HEALTH_REASON, _('Health')),
        (DEMOTION_REASON.NO_LONGER_WANTS_ROLE_REASON, _('No longer wants role')),
        (DEMOTION_REASON.REPRIMAND_REASON, _('Reprimand')),
        (DEMOTION_REASON.OTHER_REASON, _('Other (Please specify)')),
    )

    TYPE_OF_CHOICES = (
        (TYPE_OF.BUSINESS, _('Business')),
        (TYPE_OF.RESIDENTIAL, _('Residential')),
        (TYPE_OF.COMMUNITY_CARES, _('Community Cares')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = AssociateManager()

    '''
    MODEL FIELDS
    '''

    # SYSTEM FIELDS

    user = models.OneToOneField(
        SharedUser,
        help_text=_('The user whom is an associate.'),
        related_name="associate",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of area coordinator this is.'),
        choices=TYPE_OF_CHOICES,
        db_index=True,
        default=TYPE_OF.RESIDENTIAL,
    )
    uuid = models.CharField(
        _("UUID"),
        help_text=_('The unique identifier we want to release to the public to identify this unique record.'),
        default=uuid.uuid4,
        editable=False,
        max_length=63, # Do not change
        unique=True,
        db_index=True,
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

    has_signed_associate_agreement = models.BooleanField(
        _("Has signed associate agreement"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the associate agreement.'),
        blank=True,
    )
    associate_agreement = models.TextField(
        _("Associate agreement"),
        help_text=_('The actual terms of associate agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    associate_agreement_signed_on = models.DateTimeField(
        _('Associate agreement signed on'),
        help_text=_('The date when the associate agreement was signed on.'),
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

    # MISC

    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch this associate belongs to.'),
        related_name="associates",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # AUDITING FIELDS

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_associates",
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
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_associates",
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
    last_modified_from_position = models.PointField(
        _("Last modified from position"),
        help_text=_('The latitude and longitude coordinates for the last modified user.'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
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
        super(Associate, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.user.get_full_name()

    def get_pretty_state(self):
        return str(dict(Associate.STATE_CHOICES).get(self.user.member.state))

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
