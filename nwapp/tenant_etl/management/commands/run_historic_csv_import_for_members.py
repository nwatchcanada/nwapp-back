# -*- coding: utf-8 -*-
import csv
import os
import sys
import re
import os.path as ospath
import codecs
import random
import string
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedOrganization, SharedUser
from tenant_foundation.models import District, Watch, AreaCoordinator, Member


"""
Run manually in console:
python manage.py run_historic_csv_import_for_members "london" ""
"""

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class Command(BaseCommand):
    help = _('Command will load up historical data for members.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('csv_prefix', nargs='+', type=str)

    def handle(self, *args, **options):
        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Importing historic tenant...'))
        )

        # Get user inputs.
        schema_name = options['schema_name'][0]
        prefix = options['csv_prefix'][0]

        # Begin importing...
        self.begin_processing(schema_name, prefix)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported historic tenant.'))
        )

    def strip_chars(self, f):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]'
                               % u'')
        head,tail = ospath.split(f)
        fin = codecs.open(f, encoding = 'utf-8')
        fout = codecs.open(head + os.path.sep + 'tmp.csv', mode = 'w', encoding = 'utf-8')
        i = 1
        stripped = 0
        for line in fin:
            new_line, count = remove_re.subn('', line)
            if count > 0:
                plur = ((count > 1) and u's') or u''
                sys.stderr.write('Line %d, removed %s character%s.\n'
                                 % (i, count, plur))

            fout.write(new_line)
            stripped = stripped + count
            i = i + 1
        sys.stderr.write('Stripped %d characters from %d lines.\n'
                         % (stripped, i))
        fin.close()
        fout.close()
        os.rename(f, head + os.path.sep + 'old_' + tail)
        os.rename(head + os.path.sep + 'tmp.csv', f)

    def get_directory(self):
        # Get the directory of this command.
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Change root location.
        directory = directory.replace("/management", "/csv")

        # Return our directory.
        return directory

    def get_filepaths(self, directory):
        """
        This function will generate the file names in a directory
        tree by walking the tree either top-down or bottom-up. For each
        directory in the tree rooted at directory top (including top itself),
        it yields a 3-tuple (dirpath, dirnames, filenames).
        """
        file_paths = []  # List which will store all of the full filepaths.

        # Walk the tree.
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.
        return file_paths  # Self-explanatory.

    def find_filepath_containing(self, text, prefix):
        # Get all the files in the directory.
        directory = self.get_directory()
        full_file_paths = self.get_filepaths(directory)

        # print(directory)
        # print(full_file_paths)

        # Iterate through all the file paths and only process files
        # with a "CSV" filename.
        for full_file_path in full_file_paths:
            if full_file_path.endswith(".csv") and prefix in full_file_path:
                if text in full_file_path:
                    return full_file_path
        return None

    def begin_processing(self, schema_name, prefix):
        # Load up the following historic data from CSV files...
        full_file_path = self.find_filepath_containing("NWL Member Data - for Bart - NWL Member Data", prefix)  # Personal Customers
        print(full_file_path)

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        try:
            franchise = SharedOrganization.objects.get(schema_name=schema_name)
        except SharedOrganization.DoesNotExist:
            raise CommandError(_('Org does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        # Begin importing...
        with open(full_file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i, row_dict in enumerate(csvreader):
                if i > 0:

                    # # Used for debugging purposes only.
                    # self.stdout.write(
                    #     self.style.SUCCESS(_('Importing WorkOrder #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Begin importing...
                    self.run_import_from_dict(franchise, row_dict, i)

    def run_import_from_dict(self, franchise, row_dict, index):
        # print(row_dict) # For debugging purposes.

        uid = row_dict[0] # Unique ID
        role = row_dict[1] #
        watch_name = row_dict[2] # Watch Name
        first_name = row_dict[3] # Ward
        last_name = row_dict[4] # Description
        unit_number = row_dict[5]
        street_number = row_dict[6]
        street_name = row_dict[7]
        street_type = row_dict[8]
        direction = row_dict[9]
        phone = row_dict[10]
        city = row_dict[11]
        province = row_dict[12]
        postal = row_dict[13]
        email = row_dict[14]

        # print("uid:", uid)
        # print("role:", role)
        # print("watch_name:", watch_name)
        # print("first_name:", first_name)
        # print("last_name:", last_name)
        # print("unit_number:", unit_number)
        # print("street_number:", street_number)
        # print("street_name:", street_name)
        # print("street_type:", street_type)
        # print("direction:", direction)
        # print("city:", city)
        # print("phone:", phone)
        # print("province:", province)
        # print("postal:", postal)
        # print("email:", email)

        watch = Watch.objects.filter(name=watch_name).first()
        if watch is None:
            # raise CommandError(_('Watch does not exist with name `%(n)s`!')%{
            #     'n': str(watch_name),
            # })
            self.stdout.write(
                self.style.ERROR(_('Watch does not exist with name `%(n)s`!')%{
                    'n': str(watch_name),
                })
            )
        else:
            # Create the user account.
            user = SharedUser.objects.filter(id=uid).first()
            if user is None:
                user = self.create_shared_user(franchise, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email)
            else:
                user = self.update_shared_user(franchise, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email)

            # Create the profile.
            if role == "Member" or role == "member":
                self.process_member(user, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email)
            elif role == "Area Coordinator" or role == "area Coordinator":
                self.process_area_coordinator(user, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email)
            else:
                raise CommandError(_('Role `%(n)s` not supported!')%{
                    'n': str(role),
                })

    def create_shared_user(self, franchise, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email):
        print("Create user")
        has_email = email != None and email != ""
        if has_email is False:
            email = franchise.schema_name + "-uid"+str(uid)+"@nwapp.ca"
        user = SharedUser.objects.create(
            id=uid,
            tenant=franchise,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            was_email_activated=True,
        )

        password = None

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(_('Successfully created shared user with ID # %(uid)s.')%{
                'uid': str(uid),
            })
        )

        return user

    def update_shared_user(self, franchise, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email):
        print("Update user")
        user = SharedUser.objects.get(id=uid)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        self.stdout.write(
            self.style.WARNING(_('Successfully updated shared user with ID # %(uid)s.')%{
                'uid': str(uid),
            })
        )
        return user

    def process_area_coordinator(self, user, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email):
        self.stdout.write(
            self.style.WARNING(_('Successfully processed area coordinator for watch `%(watch_name)s`.')%{
                'watch_name': watch_name,
            })
        )

    def process_member(self, user, uid, role, watch_name, first_name, last_name, unit_number, street_number, street_name, street_type, direction, phone, city, province, postal, email):
        self.stdout.write(
            self.style.WARNING(_('Successfully processed member for watch `%(watch_name)s`.')%{
                'watch_name': watch_name,
            })
        )
