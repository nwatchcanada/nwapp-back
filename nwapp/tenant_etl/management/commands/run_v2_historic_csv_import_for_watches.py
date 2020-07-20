# -*- coding: utf-8 -*-
import csv
import os
import sys
import re
import os.path as ospath
import codecs
from decimal import *
from django.db.models import Sum
from django.db import IntegrityError
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation.models import SharedOrganization
from tenant_foundation.models import District, Watch, StreetAddressRange


"""
Run manually in console:
python manage.py run_v2_historic_csv_import_for_watches "london" "prod"
"""

CSV_FILENAME = "watches"


class Command(BaseCommand):
    help = _('Command will load up historical data for watches.')

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
        full_file_path = self.find_filepath_containing(CSV_FILENAME, prefix)  # Personal Customers
        # print(full_file_path)

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
                    self.run_import_from_dict(row_dict, i)

    def get_street_type_code(self, street_type):
        if street_type == StreetAddressRange.STREET_TYPE.AVENUE:
            return StreetAddressRange.STREET_TYPE.AVENUE
        elif street_type == StreetAddressRange.STREET_TYPE.DRIVE:
            return StreetAddressRange.STREET_TYPE.DRIVE
        elif street_type == StreetAddressRange.STREET_TYPE.ROAD:
            return StreetAddressRange.STREET_TYPE.ROAD
        elif street_type == StreetAddressRange.STREET_TYPE.STREET:
            return StreetAddressRange.STREET_TYPE.STREET
        elif street_type == StreetAddressRange.STREET_TYPE.WAY:
            return StreetAddressRange.STREET_TYPE.WAY
        else:
            return StreetAddressRange.STREET_TYPE.OTHER

    def get_street_direction_code(self, street_direction):
        if street_direction == StreetAddressRange.STREET_DIRECTION.EAST:
            return StreetAddressRange.STREET_DIRECTION.EAST
        elif street_direction == StreetAddressRange.STREET_DIRECTION.NORTH:
            return StreetAddressRange.STREET_DIRECTION.NORTH
        elif street_direction == StreetAddressRange.STREET_DIRECTION.NORTH_EAST:
            return StreetAddressRange.STREET_DIRECTION.NORTH_EAST
        elif street_direction == StreetAddressRange.STREET_DIRECTION.NORTH_WEST:
            return StreetAddressRange.STREET_DIRECTION.NORTH_WEST
        elif street_direction == StreetAddressRange.STREET_DIRECTION.SOUTH:
            return StreetAddressRange.STREET_DIRECTION.SOUTH
        elif street_direction == StreetAddressRange.STREET_DIRECTION.SOUTH_EAST:
            return StreetAddressRange.STREET_DIRECTION.SOUTH_EAST
        elif street_direction == StreetAddressRange.STREET_DIRECTION.SOUTH_WEST:
            return StreetAddressRange.STREET_DIRECTION.SOUTH_WEST
        elif street_direction == StreetAddressRange.STREET_DIRECTION.WEST:
            return StreetAddressRange.STREET_DIRECTION.WEST
        else:
            return StreetAddressRange.STREET_DIRECTION.NONE

    def get_street_number_range_type_code(self, street_number_range_type):
        s = str(street_number_range_type).upper()
        if s == "ALL":
            return StreetAddressRange.STREET_NUMBER_RANGE_TYPE.ALL
        elif s == "ODD":
            return StreetAddressRange.STREET_NUMBER_RANGE_TYPE.ODD
        elif s == "EVEN":
            return StreetAddressRange.STREET_NUMBER_RANGE_TYPE.EVEN
        elif s == "":
            return StreetAddressRange.STREET_NUMBER_RANGE_TYPE.ALL
        else:
            raise CommandError(_('`street_number_range_type` does not exist! %(r)s')%{ 'r': s })

    def run_import_from_dict(self, row_dict, index):
        # print(row_dict, index) # For debugging purposes only.

        # for w in Watch.objects.all():
        #     print("Delete", w.name)
        #     w.delete()
        # exit()

        numb = row_dict[0] # Watch #
        name = row_dict[1] # Watch Name
        ward = row_dict[2] # Ward
        district = row_dict[3] # District
        district_notes = row_dict[4]
        start = int(row_dict[5])
        finish = int(row_dict[6])
        street_name = row_dict[7]
        street_type = row_dict[8]
        street_type_other = None
        street_direction = row_dict[9]
        range_type = row_dict[10]

        # print("#:",numb)
        # print("name:",name)
        # print("ward:",ward)
        # print("district:", district)
        # print("district_notes:", district_notes)
        # print("start:",start)
        # print("finish:",finish)
        # print("street_name:", street_name)
        # print("street_type:", street_type)
        # print("street_direction:", street_direction)
        # print("range_type:", range_type)
        # print()

        # Specified `type_of` field.
        type_of = None
        if district == "Residential":
            type_of = Watch.TYPE_OF.RESIDENTIAL
        elif district == "Commercial":
            type_of = Watch.TYPE_OF.BUSINESS
        else:
            type_of = Watch.TYPE_OF.COMMUNITY_CARES

        # Get street range type.
        street_number_range_type = self.get_street_number_range_type_code(range_type)

        # Get district
        district = District.objects.filter(name=ward).first()
        if district is None:
            raise CommandError(_('Could not find district with name `%(name)s`.')%{
                'name': ward,
            })

        street_type_code = self.get_street_type_code(street_type)
        street_type_other = ""
        if street_type_code == StreetAddressRange.STREET_TYPE.OTHER:
            street_type_other = street_type
        street_direction = self.get_street_direction_code(street_direction)

        """
        The following code will either create or update a `Watch.`
        """
        watch = Watch.objects.filter(id=numb).first()
        if watch is None:
            try:
                watch = Watch.objects.create(
                    name = name,
                    description = district_notes,
                    district = district,
                    type_of = type_of,
                )
                self.stdout.write(
                    self.style.SUCCESS(_('Successfully created watch with ID # %(uid)s with name %(n)s.')%{
                        'uid': str(watch.id),
                        'n': name,
                    })
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(_('Failed creating watch with ID # %(uid)s with name %(n)s because %(e)s.')%{
                        'uid': numb,
                        'n': name,
                        'e': str(e)
                    })
                )
                return

        """
        The following code will either create or update a `Street Address Range.`
        """
        sar = StreetAddressRange.objects.filter(
            watch=watch,
            street_number_start = start,
            street_number_end = finish,
            street_name = street_name,
            street_number_range_type = street_number_range_type,
            street_type = street_type_code,
            street_type_other = street_type_other,
            street_direction = street_direction,
        ).first()
        if sar is None:
            sar = StreetAddressRange.objects.create(
                watch=watch,
                street_number_start = start,
                street_number_end = finish,
                street_name = street_name,
                street_number_range_type = street_number_range_type,
                street_type = street_type_code,
                street_type_other = street_type_other,
                street_direction = street_direction,
            )
            self.stdout.write(
                self.style.SUCCESS(_('Successfully created watch street address with ID # %(uid)s inside watch %(n)s.')%{
                    'uid': str(sar.id),
                    'n': name,
                })
            )


        if row_dict[0] == "":
            exit()
