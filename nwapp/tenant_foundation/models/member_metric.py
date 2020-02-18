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
        items = MemberMetric.objects.iterator(chunk_size=50)
        for item in items.all():
            item.delete()


class MemberMetric(models.Model):
    """
    Class model represents the metrics details for the member of a
    particular tenant.
    """

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'nwapp_member_metrics'
        verbose_name = _('Member Metric')
        verbose_name_plural = _('Members Metrics')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class MEMBER_VOLUNTEER:
        YES = 1
        NO = 0
        MAYBE = 2

    class MEMBER_GENDER:
        MALE = 1
        FEMALE = 2
        PREFER_NOT_TO_SAY = 3

    '''
    CHOICES
    '''

    MEMBER_VOLUNTEER_CHOICES = (
        (MEMBER_VOLUNTEER.YES, _('Yes')),
        (MEMBER_VOLUNTEER.NO, _('No')),
        (MEMBER_VOLUNTEER.MAYBE, _('Maybe')),
    )

    MEMBER_GENDER_CHOICES = (
        (MEMBER_GENDER.MALE, _('Male')),
        (MEMBER_GENDER.FEMALE, _('Female')),
        (MEMBER_GENDER.PREFER_NOT_TO_SAY, _('Prefer not to say')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = MemberManager()

    '''
    MODEL FIELDS
    '''

    member = models.OneToOneField(
        "Member",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="metric"
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this member.'),
        blank=True,
        related_name="member_metric_tags"
    )
    how_did_you_hear = models.ForeignKey(
        'HowHearAboutUsItem',
        help_text=_('How the member heard about the NWApp.'),
        blank=True,
        null=True,
        related_name="member_metric_how_did_you_hear_items",
        on_delete=models.SET_NULL
    )
    how_did_you_hear_other = models.CharField(
        _("Learned about us (other)"),
        max_length=2055,
        help_text=_('How member heared/learned about this NWApp.'),
        blank=True,
        null=True,
        default="Did not answer"
    )
    expectation = models.ForeignKey(
        'ExpectationItem',
        help_text=_('What do you expect from NW?'),
        blank=True,
        null=True,
        related_name="member_metric_expectations",
        on_delete=models.CASCADE
    )
    expectation_other = models.CharField(
        _("What do you expect from NW? (other)"),
        max_length=2055,
        help_text=_('-'),
        blank=True,
        null=True,
        default="Did not answer"
    )
    meaning = models.ForeignKey(
        'MeaningItem',
        help_text=_('What does NW mean to you?'),
        blank=True,
        null=True,
        related_name="member_metric_meanings",
        on_delete=models.SET_NULL
    )
    meaning_other = models.CharField(
        _("What does NW mean to you? (other)"),
        max_length=2055,
        help_text=_('-'),
        blank=True,
        null=True,
        default="Did not answer"
    )
    gender = models.PositiveSmallIntegerField(
        _("Gender"),
        help_text=_('Gender of the person. While `Male` and `Female` may be used, text strings are also acceptable for people who do not identify as a binary gender.'),
        blank=True,
        default=MEMBER_GENDER.PREFER_NOT_TO_SAY,
        choices=MEMBER_GENDER_CHOICES,
    )
    willing_to_volunteer = models.PositiveSmallIntegerField(
        _("Willing to willing_to_volunteer?"),
        help_text=_('Are you willing to willing_to_volunteer as a area coordinator / associate'),
        blank=True,
        default=MEMBER_VOLUNTEER.MAYBE,
        choices=MEMBER_VOLUNTEER_CHOICES,
    )
    another_household_member_registered = models.BooleanField(
        _("Another Household Member Registered?"),
        help_text=_('Is there another member of your household which is registered with us?'),
        default=False,
        null=True,
    )
    year_of_birth = models.PositiveSmallIntegerField(
        _("Year of Birth"),
        help_text=_('The year that this member was born in.'),
        blank=True,
        default=0,
    )
    total_household_count = models.PositiveSmallIntegerField(
        _("Total Household Count"),
        help_text=_('How many people are in your household?'),
        blank=True,
        null=True,
    )
    over_18_years_household_count = models.PositiveSmallIntegerField(
        _("Under 18 Years Household Count"),
        help_text=_('How many people in your household are under the age of 18?'),
        blank=True,
        null=True,
    )
    organization_employee_count = models.PositiveSmallIntegerField(
        _("Organization Employee Count"),
        help_text=_('The employee count at this member\'s organization.'),
        null=True,
        blank=True,
    )
    organization_founding_year = models.PositiveSmallIntegerField(
        _("Organization Founding Year"),
        help_text=_('The year this organization was founded.'),
        null=True,
        blank=True,
    )
    is_aboriginal = models.BooleanField(
        _("Is Aboriginal"),
        help_text=_('Is member an aborinal?'),
        default=False,
        blank=True,
        null=True,
    )
    is_transgender = models.BooleanField(
        _("Is Transgender Individual"),
        help_text=_('Is member a transgender individual?'),
        default=False,
        blank=True,
        null=True,
    )
    is_visible_minority = models.BooleanField(
        _("Is Visible Minority"),
        help_text=_('Is member a visible minority?'),
        default=False,
        blank=True,
        null=True,
    )
    is_disabled_or_has_barriers = models.BooleanField(
        _("Is Disabled Or Has Barriers"),
        help_text=_('Is member disabled or has physical barriers?'),
        default=False,
        blank=True,
        null=True,
    )
    is_over_fifty_five = models.BooleanField(
        _("Is Over 55"),
        help_text=_('Is member over 55?'),
        default=False,
        blank=True,
        null=True,
    )

    # AUDITING FIELDS

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_member_metrics",
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
    last_modified_at = models.DateTimeField(auto_now=True)
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_member_metrics",
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
        for tag in self.tags.all():
            text += str(tag) + ", "
        text += str(self.how_did_you_hear)
        text += ", " + str(self.how_did_you_hear_other)
        text += ", " + str(self.expectation)
        text += ", " + str(self.expectation_other)
        text += ", " + str(self.meaning)
        text += ", " + str(self.meaning_other)
        text += ", " + str(self.year_of_birth)
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
            try:
                latest_obj = MemberMetric.objects.latest('id');
                self.id = latest_obj.id + 1
            except MemberContact.DoesNotExist:
                self.id = 1

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(MemberMetric, self).save(*args, **kwargs)

    def get_pretty_gender(self):
        return str(dict(MemberMetric.MEMBER_GENDER_CHOICES).get(self.gender))

    def get_pretty_willing_to_volunteer(self):
        return str(dict(MemberMetric.MEMBER_VOLUNTEER_CHOICES).get(self.willing_to_volunteer))
