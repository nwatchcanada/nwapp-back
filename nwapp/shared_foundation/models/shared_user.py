# -*- coding: utf-8 -*-
"""user.py

The class model to represent the user in our application. This class overrides
default ``User`` model provided by ``Django`` to support the following:

TODO
"""
from __future__ import unicode_literals
import uuid
import os
from binascii import hexlify
from pytz import timezone as pytz_timezone
from datetime import date, datetime, timedelta
from django.db import models
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from faker import Faker

from shared_foundation import constants
from shared_foundation.models.shared_group import SharedGroup


def _createHash():
    return hexlify(os.urandom(16))


def get_expiry_date(days=2):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


def get_referral_code():
    return get_random_string(
        length=31,
        allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'
    )


class SharedUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):  #TODO: UNIT TEST
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def delete_all(self):
        try:
            for user in SharedUser.objects.iterator(chunk_size=500):
                user.delete()
        except Exception as e:
            print(e)

    def seed(self, length=25):
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                first_name = faker.first_name()
                last_name = faker.last_name()
                user = SharedUser.objects.create(
                    email = faker.safe_email(),
                    first_name = first_name,
                    middle_name = None,
                    last_name = last_name,
                )
                results.append(user)
            except Exception as e:
                pass
        return results


class SharedUser(AbstractBaseUser, PermissionsMixin):

    '''
    Constants & choices
    '''

    class REPORT_EMAIL_FREQUENCY:
        NEVER = 1
        WEEKLY = 2
        MONTHLY = 3

    REPORT_EMAIL_FREQUENCY_CHOICES = (
        (REPORT_EMAIL_FREQUENCY.NEVER, _('Never')),
        (REPORT_EMAIL_FREQUENCY.WEEKLY, _('Weekly')),
        (REPORT_EMAIL_FREQUENCY.MONTHLY, _('Monthly')),
    )

    '''
    Fields
    '''

    #
    # SYSTEM UNIQUE IDENTIFIER & TENANCY
    #

    tenant = models.ForeignKey(
        "SharedOrganization",
        help_text=_('The tenant this user belongs to.'),
        related_name="users",
        on_delete=models.CASCADE
    )
    email = models.EmailField( # THIS FIELD IS REQUIRED.
        _("Email"),
        help_text=_('Email address.'),
        db_index=True,
        unique=True
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique identifier used externally.'),
        null=False,
        unique=True,
        db_index=True,
    )

    #
    # PERSON FIELDS - http://schema.org/Person
    #
    first_name = models.CharField(
        _("First Name"),
        max_length=63,
        help_text=_('The users given name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The users middle name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The users last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    #
    # REPORT EMAIL FREQUENCY FIELD
    #

    report_email_frequency = models.PositiveSmallIntegerField(
        _("Report email frequency"),
        help_text=_('The frequency to email the report by.'),
        blank=True,
        null=False,
        default=REPORT_EMAIL_FREQUENCY.WEEKLY,
        choices=REPORT_EMAIL_FREQUENCY_CHOICES,
    )
    last_report_email_created_at = models.DateTimeField(
        _('Last report email created at'),
        help_text=_('The date and time of the last report email was created.'),
        blank=True,
        null=True
    )

    #
    # SYSTEM FIELD
    #

    timezone = models.CharField(
        _("Timezone"),
        max_length=63,
        help_text=_('The timezone the user belongs to.'),
        blank=True,
        default='UTC',
        choices=constants.TIMEZONE_CHOICES
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        blank=True
    )
    is_staff = models.BooleanField(
        _('Is Staff'),
        help_text=_('Variable conrols whether this user has permission to access the <strong>Django administration</strong>.'),
        default=False,
        blank=True
    )
    is_superuser = models.BooleanField(
        _('Is Superuser'),
        default=False,
        blank=True
    )
    salt = models.CharField( #DEVELOPERS NOTE: Used for cryptographic signatures.
        _("Salt"),
        max_length=127,
        help_text=_('The unique salt value me with this object.'),
        default=_createHash,
        unique=True,
        blank=True,
        null=True
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of user this is. Value represents ID of user type.'),
        default=0,
        blank=True,
        db_index=True,
    )
    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether customer allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether customer allows being reached by text.'),
        default=True,
        blank=True
    )
    location = PointField(
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this user.'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    #
    #  Referral Program
    #

    referral_code = models.CharField(
        _("Referral Code"),
        help_text=_('The referral code which can be given out to other users.'),
        max_length=31,
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        default=get_referral_code
    )
    referred_by = models.ForeignKey(
        "self",
        help_text=_('The user whom referred this user into our system.'),
        blank=True,
        null=True,
        related_name="referrals",
        on_delete=models.SET_NULL
    )


    #
    # EMAIL ACTIVATION FIELD
    #

    was_email_activated = models.BooleanField(
        _("Was Email Activated"),
        help_text=_('Was the email address verified?'),
        default=False,
        blank=True
    )

    #
    # ONBOARDING FIELD
    #

    was_onboarded = models.BooleanField(
        _("Was Onboarded"),
        help_text=_('Was the user onboarded in our system? If yes then allow user access to their dashboard and the remaining features of the site.'),
        default=False,
        blank=True
    )
    onboarding_survey_data = JSONField(
        _("Survey data"),
        help_text=_('The onboarding submitted survey data.'),
        blank=True,
        null=True,
    )

    #
    # PASSWORD RESET FIELDS
    #

    pr_access_code = models.CharField(
        _("Password Reset Access Code"),
        max_length=127,
        help_text=_('The access code to enter the password reset page to be granted access to restart your password.'),
        blank=True,
        default=_createHash,
    )
    pr_expiry_date = models.DateTimeField(
        _('Password Reset Access Code Expiry Date'),
        help_text=_('The date where the access code expires and no longer works.'),
        blank=True,
        default=get_expiry_date,
    )

    #
    #  Terms of Service Legal Agreement
    #

    has_signed_tos = models.BooleanField(
        _("Has signed terms of service"),
        default=False,
        help_text=_('Boolean indicates whether has agreed to the terms of service.'),
        blank=True,
    )
    tos_agreement = models.TextField(
        _("Terms of service agreement"),
        help_text=_('The actual terms of service agreement the user agreed to when they signed.'),
        blank=True,
        null=True,
    )
    tos_signed_on = models.DateTimeField(
        _('Terms of service signed on'),
        help_text=_('The date where the access code expires and no longer works.'),
        blank=True,
        null=True,
    )

    '''
    Object Manager
    '''

    objects = SharedUserManager()

    '''
    User field objects
    '''

    # DEVELOPERS NOTE:
    # WE WILL BE USING "EMAIL" AND "ACADEMY" AS THE UNIQUE PAIR THAT WILL
    # DETERMINE WHETHER THE AN ACCOUNT EXISTS. WE ARE DOING THIS TO SUPPORT
    # TENANT SPECIFIC USER ACCOUNTS WHICH DO NOT EXIST ON OTHER TENANTS.
    # WE USE CUSTOM "AUTHENTICATION BACKEND" TO SUPPORT THE LOGGING IN.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'is_staff',
        'is_active',
        'is_superuser',
    ]

    '''
    Metadata
    '''

    class Meta:
        app_label = 'shared_foundation'
        db_table = 'nwapp_shared_users'
        verbose_name = _('Shared User')
        verbose_name_plural = _('Shared Users')
        default_permissions = ()
        permissions = ()

    '''
    Functions
    '''

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''
        Override the `save` function to support extra functionality of our model.
        '''

        if self.slug == None or self.slug == "":
            #TOOD: IMPLEMENT IN FUTURE:
            #TODO: HANDLE THE CASE WHEN EDITING IS BEING MADE.
            #TODO: HANDLE CASE IF FIRST/LAST NAMES ARE NOT UNIQUE.
            self.slug = slugify(self.user.get_full_name())+"-"+str(self.user.id)

        '''
        Finally call the parent function which handles saving so we can carry
        out the saving operation by Django in our ORM.
        '''
        super(SharedUser, self).save(*args, **kwargs)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name  #TODO: UNIT TEST

    def __str__(self):
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)  #TODO: UNIT TEST

    def generate_pr_code(self):
        """
        Function generates a new password reset code and expiry date.
        """
        self.pr_access_code = get_random_string(length=127)
        self.pr_expiry_date = get_expiry_date()
        self.save()
        return self.pr_access_code

    def has_pr_code_expired(self):
        """
        Returns true or false depending on whether the password reset code
        has expired or not.
        """
        today = timezone.now()
        return today >= self.pr_expiry_date

    def get_dashboard_path(self):
        """
        Function will return either the onbarding PATH or the dashboard PATH
        based on whether the user was "onboarded" or not.
        """
        if self.was_onboarded:
            return "/dashboard"
        else:
            return "/onboard"

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'is_executive':
                del self.draft_invoice
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def get_now(self):
        user_timezone = pytz_timezone(self.timezone)
        now_utc = datetime.now(pytz_timezone('UTC'))
        return now_utc.astimezone(user_timezone)

    @cached_property
    def is_executive(self):
        """
        Returns either True or False depending on if this user belongs to the
        executive group.
        """
        return self.groups.filter(id=SharedGroup.GROUP_MEMBERSHIP.EXECUTIVE).exists()
