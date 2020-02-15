# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import (
    Tag, HowHearAboutUsItem, ExpectationItem, MeaningItem, ItemType
)


class Command(BaseCommand):
    help = _('Command will populate tenant specific data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py populate_tenant_content "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]

        try:
            organization = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Organization does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(organization.schema_name, True) # Switch to Tenant.

        # Update content.
        self.populate_default_tags()
        self.populate_default_how_did_you_hear_items()
        self.populate_default_expectation_items()
        self.populate_default_meaning_items()
        self.populate_default_item_type_items()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated tenant content.'))
        )

    def populate_default_tags(self):
        DATA_ARRAY = [
            # ID | TEXT | DESCRIPTION | IS ARCHIVED |
            #-------------------------------------------------------------------
            [1, "Aboriginal", 'Please use this tag if something is related to aboriginal topics.', False, ],
            [2, "First Responder", 'Please use this tag if something is related to first responder topics.', False, ],
            [3, "Veteran", 'Please use this tag if something is related to veteran topics.', False, ],
            [4, "Police Officer", 'Please use this tag if something is related to police officer topics.', False, ],
            [5, "Doctor", 'Please use this tag if something is related to doctor topics.', False, ],
            [6, "Nurse", 'Please use this tag if something is related to nurse topics.', False, ],
            [7, "Teacher", 'Please use this tag if something is related to teacher topics.', False, ],
            [8, "Armed Forces Member", 'Please use this tag if something is related to armed forces member topics.', False, ],
        ]
        for data_arr in DATA_ARRAY:
            Tag.objects.update_or_create(
                id=int(data_arr[0]),
                defaults={
                    'id': int(data_arr[0]),
                    'text': data_arr[1],
                    'description': data_arr[2],
                    'is_archived': data_arr[3],
                }
            )

    def populate_default_how_did_you_hear_items(self):
        DATA_ARRAY = [
            # ID | SORT # | TEXT | ASSOCIATE | CUSTOMER | STAFF | PARTNER
            #-------------------------------------------------------------------
            # Associate
            [1, 99,"Other",                            True, True,  True,  True,],
            [2, 2, "An existing member",               True, False, False, False,],
            [3, 3, "Print Ad",                         True, False, False, False,],
            [4, 4, "Online Ad",                        True, False, False, False,],
            [5, 5, "Google",                           True, False, False, False,],
            [6, 6, "Tradeshow/Event",                  True, False, False, False,],
            [7, 7, "Agency",                           True, False, False, False,],
            [8, 8, "Prefer not to say / I don't know", True, False, False, False,],

            # Customer
            [9, 2, "A friend or family member",  False, True, False, False,],
            [10, 5, "An Over 55 Associate",      False, True, False, False,],
            [11, 6, "Facebook",                  False, True, False, False,],
            [12, 7, "Twitter",                   False, True, False, False,],
            [13, 8, "Instagram",                 False, True, False, False,],
            [14, 11, "Home & Outdoor Show",      False, True, False, False,],
            [15, 12, "Western Fair",             False, True, False, False,],
            [16, 13, "Rib Fest",                 False, True, False, False,],
            [17, 14, "Coffee News",              False, True, False, False,],
            [18, 15, "Business London Magazine", False, True, False, False,],
        ]

        for data_arr in DATA_ARRAY:
            HowHearAboutUsItem.objects.update_or_create(
                id=int(data_arr[0]),
                defaults={
                    'id': int(data_arr[0]),
                    'sort_number': int(data_arr[1]),
                    'text': data_arr[2],
                    'is_for_associate': data_arr[3],
                    'is_for_customer': data_arr[4],
                    'is_for_staff': data_arr[5],
                    'is_for_partner': data_arr[6],
                }
            )

    def populate_default_expectation_items(self):
        DATA_ARRAY = [
            # ID | SORT # | TEXT | ASSOCIATE | CUSTOMER | STAFF | PARTNER
            #-------------------------------------------------------------------
            # Associate
            [1, 99,"Other",                                   True, True, True, True,],
            [2, 2, "Greater safety",                          True, True, True, True,],
            [3, 3, "Safety awareness & education",            True, True, True, True,],
            [4, 4, "Greater community cohesion",              True, True, True, True,],
            [5, 5, "Better relationships with my neighbours", True, True, True, True,],
            [6, 6, "A chance to help my community",           True, True, True, True,],
            [7, 7, "Crime reduction",                         True, True, True, True,],
        ];

        for data_arr in DATA_ARRAY:
            ExpectationItem.objects.update_or_create(
                id=int(data_arr[0]),
                defaults={
                    'id': int(data_arr[0]),
                    'sort_number': int(data_arr[1]),
                    'text': data_arr[2],
                    'is_for_associate': data_arr[3],
                    'is_for_customer': data_arr[4],
                    'is_for_staff': data_arr[5],
                    'is_for_partner': data_arr[6],
                }
            )

    def populate_default_meaning_items(self):
        DATA_ARRAY = [
            # ID | SORT # | TEXT | ASSOCIATE | CUSTOMER | STAFF | PARTNER
            #-------------------------------------------------------------------
            # Associate
            [1, 99,"Other",                       True, True, True, True,],
            [2, 2, "Greater community safety",    True, True, True, True,],
            [3, 3, "Greater social inclusion",    True, True, True, True,],
            [4, 4, "Caring about my neighbour",   True, True, True, True,],
            [5, 5, "Greater community vigilance", True, True, True, True,],
        ]

        for data_arr in DATA_ARRAY:
            MeaningItem.objects.update_or_create(
                id=int(data_arr[0]),
                defaults={
                    'id': int(data_arr[0]),
                    'sort_number': int(data_arr[1]),
                    'text': data_arr[2],
                    'is_for_associate': data_arr[3],
                    'is_for_customer': data_arr[4],
                    'is_for_staff': data_arr[5],
                    'is_for_partner': data_arr[6],
                }
            )

    def populate_default_item_type_items(self):
        DATA_ARRAY = [
            # ID | CATEGORY | TEXT | DESCRIPTION | IS ARCHIVED |
            #-------------------------------------------------------------------
            [2, ItemType.CATEGORY.EVENT, "NW Meeting", '', False, ],
            [3, ItemType.CATEGORY.EVENT, "Garage Sale", '', False, ],
            [4, ItemType.CATEGORY.EVENT, "Party", '', False, ],
            [5, ItemType.CATEGORY.EVENT, "Community Cleanup", '', False, ],
            [6, ItemType.CATEGORY.EVENT, "Community Consultation", '', False, ],
            [7, ItemType.CATEGORY.EVENT, "Arts Event", '', False, ],
            [8, ItemType.CATEGORY.EVENT, "Club Meeting", '', False, ],
            [9, ItemType.CATEGORY.EVENT, "Fundraiser", '', False, ],
            [102, ItemType.CATEGORY.INCIDENT, "Criminal Activity", '', False, ],
            [103, ItemType.CATEGORY.INCIDENT, "Physical Safety Hazard", '', False, ],
            [104, ItemType.CATEGORY.INCIDENT, "Suspicious Individual", '', False, ],
            [105, ItemType.CATEGORY.INCIDENT, "Mental Health Issue", '', False, ],
            [106, ItemType.CATEGORY.INCIDENT, "Addiction Issue", '', False, ],
            # [107, ItemType.CATEGORY.EVENT, "-", '', False, ],
        ];
        for data_arr in DATA_ARRAY:
            ItemType.objects.update_or_create(
                id=int(data_arr[0]),
                defaults={
                    'id': int(data_arr[0]),
                    'category': int(data_arr[1]),
                    'text': data_arr[2],
                    'description': data_arr[3],
                    'is_archived': data_arr[4],
                }
            )
