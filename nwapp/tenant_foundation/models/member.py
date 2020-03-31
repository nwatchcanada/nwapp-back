import phonenumbers
from random import randint
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.validators import EmailValidator
from django.contrib.gis.db import models
from django.db.models import Q
from django.db import transaction
from django.db.models.aggregates import Count
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from shared_foundation.models import SharedUser
from shared_foundation.utils import get_point_from_ip

# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


class MemberManager(models.Manager):
    def delete_all(self):
        items = Member.objects.iterator(chunk_size=1000)
        for item in items:
            item.user.delete()

    def search(self, keyword):
        """Default search algorithm used for this model."""
        return self.partial_text_search(keyword)

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

    def random(self):
        """
        Function will get a single random object from the datbase.
        Special thanks via: https://stackoverflow.com/a/2118712
        """
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


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

    # MISC FIELDS

    avatar_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The avatar image of this member.'),
        related_name="members",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    watch = models.ForeignKey(
        "Watch",
        help_text=_('The watch this member belongs to.'),
        related_name="members",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
        return self.user.get_full_name()

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''
        if self.created_from:
            self.created_from_position = get_point_from_ip(self.created_from)
        if self.last_modified_from:
            self.last_modified_from_position = get_point_from_ip(self.last_modified_from)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(Member, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.user.get_full_name()

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

    @staticmethod
    def get_searchable_content(member):
        """
        Utility function which refreshes the searchable content used when
        searching for `keywords`.
        """
        text = member.user.slug + " "
        if member.contact:
            text += member.contact.get_searchable_content()
        if member.address:
            text += " " + member.address.get_searchable_content()
        if member.metric:
            text += " " + member.metric.get_searchable_content()
        if member.watch:
            text += " " + member.watch.get_searchable_content()
        return text

    @staticmethod
    def seed(tenant, length=25):
        from faker import Faker
        from shared_foundation.models import SharedUser, SharedGroup
        from tenant_foundation.models import Member
        from tenant_foundation.models import MemberAddress
        from tenant_foundation.models import MemberContact
        from tenant_foundation.models import MemberMetric
        from tenant_foundation.models import MemberComment
        from tenant_foundation.models import Watch
        from tenant_foundation.models import StreetAddressRange
        from tenant_foundation.models import HowHearAboutUsItem
        from tenant_foundation.models import ExpectationItem
        from tenant_foundation.models import MeaningItem
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                first_name = faker.first_name()
                last_name = faker.last_name()
                street_address = StreetAddressRange.objects.random()
                organization_name = faker.company()
                organization_type_of = faker.pyint(min_value=2, max_value=4, step=1)
                user = SharedUser.objects.create(
                    tenant=tenant,
                    email = faker.safe_email(),
                    first_name = first_name,
                    middle_name = None,
                    last_name = last_name,
                )
                user.groups.add(SharedGroup.GROUP_MEMBERSHIP.MEMBER)
                member = Member.objects.create(
                    user=user,
                    type_of=street_address.watch.type_of,
                    watch=street_address.watch,
                )
                member_contact = MemberContact.objects.create(
                    member=member,
                    is_ok_to_email=True,
                    is_ok_to_text=True,
                    organization_name=organization_name,
                    organization_type_of=organization_type_of,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    primary_phone=faker.phone_number(),
                    secondary_phone=faker.phone_number(),
                )
                member_address = MemberAddress.objects.create(
                    member=member,
                    country="Canada",
                    province="Ontario",
                    city=faker.city(),
                    street_number=faker.pyint(
                        min_value=street_address.street_number_start,
                        max_value=street_address.street_number_end,
                        step=1
                    ),
                    street_name=street_address.street_name,
                    apartment_unit=faker.pyint(
                        min_value=1,
                        max_value=1000,
                        step=1
                    ),
                    street_type=street_address.street_type,
                    street_type_other=street_address.street_type_other,
                    street_direction=street_address.street_direction,
                    postal_code=faker.postalcode(),
                )
                member_metric = MemberMetric.objects.create(
                    member = member,
                    how_did_you_hear = HowHearAboutUsItem.objects.random(),
                    how_did_you_hear_other = faker.company(),
                    expectation = ExpectationItem.objects.random(),
                    expectation_other = faker.company(),
                    meaning = MeaningItem.objects.random(),
                    meaning_other = faker.company(),
                    # gender=
                    # willing_to_volunteer=
                    another_household_member_registered=False,
                    year_of_birth=faker.pyint(min_value=1920, max_value=1990, step=1),
                    total_household_count=faker.pyint(min_value=2, max_value=6, step=1),
                    over_18_years_household_count = faker.pyint(min_value=0, max_value=1, step=1),
                    organization_employee_count = faker.pyint(min_value=0, max_value=10, step=1),
                    organization_founding_year=faker.pyint(min_value=1920, max_value=1990, step=1),
                )
                results.append(member)
            except Exception as e:
                print(e)
                pass
        return results


    def promote_to_area_coordinator(self, defaults):
        """
        - defaults
            - has_signed_area_coordinator_agreement
            - has_signed_conflict_of_interest_agreement
            - has_signed_code_of_conduct_agreement
            - has_signed_confidentiality_agreement
            - police_check_date
            - created_by
            - created_from
            - created_from_is_public
            - last_modified_by
            - last_modified_from
            - last_modified_from_is_public
        """
        from django.template.loader import render_to_string  # HTML / TXT
        from django.utils import timezone
        from shared_foundation.models import SharedGroup
        from tenant_foundation.models import AreaCoordinator

        has_signed_area_coordinator_agreement = defaults.get('has_signed_area_coordinator_agreement', None)
        has_signed_conflict_of_interest_agreement = defaults.get('has_signed_conflict_of_interest_agreement', None)
        has_signed_code_of_conduct_agreement = defaults.get('has_signed_code_of_conduct_agreement', None)
        has_signed_confidentiality_agreement = defaults.get('has_signed_confidentiality_agreement', None)
        police_check_date = defaults.get('police_check_date', None)
        created_by = defaults.get('created_by', None)
        created_from = defaults.get('created_from', None)
        created_from_is_public = defaults.get('created_from_is_public', None)
        last_modified_by = defaults.get('last_modified_by', None)
        last_modified_from = defaults.get('last_modified_from', None)
        last_modified_from_is_public = defaults.get('last_modified_from_is_public', None)

        # Defensive code.
        assert self.user != None
        assert isinstance(has_signed_area_coordinator_agreement, bool)
        assert isinstance(has_signed_conflict_of_interest_agreement, bool)
        assert isinstance(has_signed_code_of_conduct_agreement, bool)
        assert isinstance(has_signed_confidentiality_agreement, bool)
        assert police_check_date != None

        # Get the text agreement which will be signed.
        area_coordinator_agreement = render_to_string('account/area_coordinator_agreement/2019_05_01.txt', {}) if has_signed_area_coordinator_agreement else None
        conflict_of_interest_agreement = render_to_string('account/conflict_of_interest_agreement/2019_05_01.txt', {}) if has_signed_conflict_of_interest_agreement else None
        code_of_conduct_agreement = render_to_string('account/code_of_conduct_agreement/2019_05_01.txt', {}) if has_signed_code_of_conduct_agreement else None
        confidentiality_agreement = render_to_string('account/confidentiality_agreement/2019_05_01.txt', {}) if has_signed_confidentiality_agreement else None

        # Create or update our model.
        area_coordinator, created = AreaCoordinator.objects.update_or_create(
            user=self.user,
            defaults={
                'user': self.user,
                'has_signed_area_coordinator_agreement': has_signed_area_coordinator_agreement,
                'area_coordinator_agreement': area_coordinator_agreement,
                'area_coordinator_agreement_signed_on': timezone.now(),
                'has_signed_conflict_of_interest_agreement': has_signed_conflict_of_interest_agreement,
                'conflict_of_interest_agreement': conflict_of_interest_agreement,
                'conflict_of_interest_agreement_signed_on': timezone.now(),
                'has_signed_code_of_conduct_agreement': has_signed_code_of_conduct_agreement,
                'code_of_conduct_agreement': code_of_conduct_agreement,
                'code_of_conduct_agreement_signed_on': timezone.now(),
                'has_signed_confidentiality_agreement': has_signed_confidentiality_agreement,
                'confidentiality_agreement': confidentiality_agreement,
                'confidentiality_agreement_signed_on': timezone.now(),
                'police_check_date': police_check_date,
                'created_by': created_by,
                'created_from': created_from,
                'created_from_is_public': created_from_is_public,
                'created_from_position': get_point_from_ip(created_from),
                'last_modified_by': last_modified_by,
                'last_modified_from': last_modified_from,
                'last_modified_from_is_public': last_modified_from_is_public,
                'last_modified_from_position': get_point_from_ip(last_modified_from),
            }
        )

        # Set the user's role to be a area coordinator after clearing the
        # previous group memberships.
        area_coordinator.user.groups.clear()
        area_coordinator.user.groups.add(SharedGroup.GROUP_MEMBERSHIP.AREA_COORDINATOR)

        return area_coordinator

    def promote_to_associate(self, defaults):
        """
        - defaults
            - has_signed_associate_agreement
            - has_signed_conflict_of_interest_agreement
            - has_signed_code_of_conduct_agreement
            - has_signed_confidentiality_agreement
            - police_check_date
            - created_by
            - created_from
            - created_from_is_public
            - last_modified_by
            - last_modified_from
            - last_modified_from_is_public
        """
        from django.template.loader import render_to_string  # HTML / TXT
        from django.utils import timezone
        from shared_foundation.models import SharedGroup
        from tenant_foundation.models import Associate

        has_signed_associate_agreement = defaults.get('has_signed_associate_agreement', None)
        has_signed_conflict_of_interest_agreement = defaults.get('has_signed_conflict_of_interest_agreement', None)
        has_signed_code_of_conduct_agreement = defaults.get('has_signed_code_of_conduct_agreement', None)
        has_signed_confidentiality_agreement = defaults.get('has_signed_confidentiality_agreement', None)
        police_check_date = defaults.get('police_check_date', None)
        created_by = defaults.get('created_by', None)
        created_from = defaults.get('created_from', None)
        created_from_is_public = defaults.get('created_from_is_public', None)
        last_modified_by = defaults.get('last_modified_by', None)
        last_modified_from = defaults.get('last_modified_from', None)
        last_modified_from_is_public = defaults.get('last_modified_from_is_public', None)

        # Defensive code.
        assert self.user != None
        assert isinstance(has_signed_associate_agreement, bool)
        assert isinstance(has_signed_conflict_of_interest_agreement, bool)
        assert isinstance(has_signed_code_of_conduct_agreement, bool)
        assert isinstance(has_signed_confidentiality_agreement, bool)
        assert police_check_date != None

        # Get the text agreement which will be signed.
        associate_agreement = render_to_string('account/associate_agreement/2019_05_01.txt', {}) if has_signed_associate_agreement else None
        conflict_of_interest_agreement = render_to_string('account/conflict_of_interest_agreement/2019_05_01.txt', {}) if has_signed_conflict_of_interest_agreement else None
        code_of_conduct_agreement = render_to_string('account/code_of_conduct_agreement/2019_05_01.txt', {}) if has_signed_code_of_conduct_agreement else None
        confidentiality_agreement = render_to_string('account/confidentiality_agreement/2019_05_01.txt', {}) if has_signed_confidentiality_agreement else None

        # Create or update our model.
        associate, created = Associate.objects.update_or_create(
            user=self.user,
            defaults={
                'user': self.user,
                'has_signed_associate_agreement': has_signed_associate_agreement,
                'associate_agreement': associate_agreement,
                'associate_agreement_signed_on': timezone.now(),
                'has_signed_conflict_of_interest_agreement': has_signed_conflict_of_interest_agreement,
                'conflict_of_interest_agreement': conflict_of_interest_agreement,
                'conflict_of_interest_agreement_signed_on': timezone.now(),
                'has_signed_code_of_conduct_agreement': has_signed_code_of_conduct_agreement,
                'code_of_conduct_agreement': code_of_conduct_agreement,
                'code_of_conduct_agreement_signed_on': timezone.now(),
                'has_signed_confidentiality_agreement': has_signed_confidentiality_agreement,
                'confidentiality_agreement': confidentiality_agreement,
                'confidentiality_agreement_signed_on': timezone.now(),
                'police_check_date': police_check_date,
                'created_by': created_by,
                'created_from': created_from,
                'created_from_is_public': created_from_is_public,
                'created_from_position': get_point_from_ip(created_from),
                'last_modified_by': last_modified_by,
                'last_modified_from': last_modified_from,
                'last_modified_from_is_public': last_modified_from_is_public,
                'last_modified_from_position': get_point_from_ip(last_modified_from),
            }
        )

        # Set the user's role to be a area coordinator after clearing the
        # previous group memberships.
        associate.user.groups.clear()
        associate.user.groups.add(SharedGroup.GROUP_MEMBERSHIP.ASSOCIATE)

        return associate

    def promote_to_staff(self, defaults):
        """
        - defaults
            - role_id
            - has_signed_staff_agreement
            - has_signed_conflict_of_interest_agreement
            - has_signed_code_of_conduct_agreement
            - has_signed_confidentiality_agreement
            - police_check_date
            - created_by
            - created_from
            - created_from_is_public
            - last_modified_by
            - last_modified_from
            - last_modified_from_is_public
        """
        from django.template.loader import render_to_string  # HTML / TXT
        from django.utils import timezone
        from shared_foundation.models import SharedGroup
        from tenant_foundation.models import Staff

        role_id = defaults.get('role_id', None)
        has_signed_staff_agreement = defaults.get('has_signed_staff_agreement', None)
        has_signed_conflict_of_interest_agreement = defaults.get('has_signed_conflict_of_interest_agreement', None)
        has_signed_code_of_conduct_agreement = defaults.get('has_signed_code_of_conduct_agreement', None)
        has_signed_confidentiality_agreement = defaults.get('has_signed_confidentiality_agreement', None)
        police_check_date = defaults.get('police_check_date', None)
        created_by = defaults.get('created_by', None)
        created_from = defaults.get('created_from', None)
        created_from_is_public = defaults.get('created_from_is_public', None)
        last_modified_by = defaults.get('last_modified_by', None)
        last_modified_from = defaults.get('last_modified_from', None)
        last_modified_from_is_public = defaults.get('last_modified_from_is_public', None)

        # Defensive code.
        assert self.user != None
        assert isinstance(role_id, int)
        assert isinstance(has_signed_staff_agreement, bool)
        assert isinstance(has_signed_conflict_of_interest_agreement, bool)
        assert isinstance(has_signed_code_of_conduct_agreement, bool)
        assert isinstance(has_signed_confidentiality_agreement, bool)
        assert police_check_date != None

        # Get the text agreement which will be signed.
        staff_agreement = render_to_string('account/staff_agreement/2019_05_01.txt', {}) if has_signed_staff_agreement else None
        conflict_of_interest_agreement = render_to_string('account/conflict_of_interest_agreement/2019_05_01.txt', {}) if has_signed_conflict_of_interest_agreement else None
        code_of_conduct_agreement = render_to_string('account/code_of_conduct_agreement/2019_05_01.txt', {}) if has_signed_code_of_conduct_agreement else None
        confidentiality_agreement = render_to_string('account/confidentiality_agreement/2019_05_01.txt', {}) if has_signed_confidentiality_agreement else None

        # Create or update our model.
        staff, created = Staff.objects.update_or_create(
            user=self.user,
            defaults={
                'user': self.user,
                'has_signed_staff_agreement': has_signed_staff_agreement,
                'staff_agreement': staff_agreement,
                'staff_agreement_signed_on': timezone.now(),
                'has_signed_conflict_of_interest_agreement': has_signed_conflict_of_interest_agreement,
                'conflict_of_interest_agreement': conflict_of_interest_agreement,
                'conflict_of_interest_agreement_signed_on': timezone.now(),
                'has_signed_code_of_conduct_agreement': has_signed_code_of_conduct_agreement,
                'code_of_conduct_agreement': code_of_conduct_agreement,
                'code_of_conduct_agreement_signed_on': timezone.now(),
                'has_signed_confidentiality_agreement': has_signed_confidentiality_agreement,
                'confidentiality_agreement': confidentiality_agreement,
                'confidentiality_agreement_signed_on': timezone.now(),
                'police_check_date': police_check_date,
                'created_by': created_by,
                'created_from': created_from,
                'created_from_is_public': created_from_is_public,
                'created_from_position': get_point_from_ip(created_from),
                'last_modified_by': last_modified_by,
                'last_modified_from': last_modified_from,
                'last_modified_from_is_public': last_modified_from_is_public,
                'last_modified_from_position': get_point_from_ip(last_modified_from),
            }
        )

        # Set the user's role to be after clearing the previous group memberships.
        staff.user.groups.clear()
        staff.user.groups.add(role_id)

        return staff
