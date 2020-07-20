from datetime import timedelta, datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedOrganization
from tenant_foundation.models import District, Watch

# Run manually in console:
# python manage.py hotfix_001


class Command(BaseCommand):
    help = _('Fixes `id` increment bug which results from the ETL imports.')

    def handle(self, *args, **options):
        connection.set_schema_to_public() # Switch to Public.
        self.apply_shared_user_table_fix()
        for franchise in SharedOrganization.objects.filter(~Q(schema_name="public")):
            connection.set_schema(franchise.schema_name, True) # Switch to Tenant.
            self.apply_tenant_district_table_fix()
            # self.apply_tenant_watches_table_fix()

        self.stdout.write(# For debugging purposes.
            self.style.SUCCESS(_('Hotfix 001: Was successfully applied.'))
        )

    def apply_shared_user_table_fix(self):
        all_count = SharedUser.objects.count()
        all_possible_range = range(all_count, all_count + 2000)

        self.stdout.write(
            self.style.SUCCESS(_('Hotfix 001: Repairing `id` in `shared_users` table for %(c)s.')%{
                'c': all_count
            })
        )

        while True:
            try:
                user = SharedUser.objects.create(tenant_id=1) # Look here!
            except Exception as e:
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: Incrementing `id` in `shared_users` table.'))
                )
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: %(e)s')%{
                        'e': str(e)
                    })
                )
                for search_id in all_possible_range:
                    if str(search_id) in str(e):
                        self.stdout.write(
                            self.style.SUCCESS(_('Hotfix 001: Successfully repaired `shared_users` table.\n'))
                        )
                        return

    def apply_tenant_district_table_fix(self):
        all_count = Watch.objects.count()
        all_possible_range = range(all_count, all_count + 2000)

        self.stdout.write(
            self.style.SUCCESS(_('Hotfix 001: Repairing `id` in `nwapp_watches` table for %(c)s.')%{
                'c': all_count
            })
        )

        while True:
            try:
                user = District.objects.create()
            except Exception as e:
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: Incrementing `id` in `nwapp_watches` table.'))
                )
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: %(e)s')%{
                        'e': str(e)
                    })
                )
                for search_id in all_possible_range:
                    if str(search_id) in str(e):
                        self.stdout.write(
                            self.style.SUCCESS(_('Hotfix 001: Successfully repaired `nwapp_watches` table.\n'))
                        )
                        return

    def apply_tenant_watches_table_fix(self):
        all_count = Watch.objects.count()
        all_possible_range = range(all_count, all_count + 2000)

        self.stdout.write(
            self.style.SUCCESS(_('Hotfix 001: Repairing `id` in `nwapp_watches` table for %(c)s.')%{
                'c': all_count
            })
        )

        while True:
            try:
                user = Watch.objects.create(
                    district=District.objects.get(id=1),
                    type_of=1,
                    name=str(all_count),
                )
            except Exception as e:
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: Incrementing `id` in `nwapp_members` table.'))
                )
                self.stdout.write(
                    self.style.SUCCESS(_('Hotfix 001: %(e)s')%{
                        'e': str(e)
                    })
                )
                for search_id in all_possible_range:
                    if str(search_id) in str(e):
                        self.stdout.write(
                            self.style.SUCCESS(_('Hotfix 001: Successfully repaired `nwapp_members` table.\n'))
                        )
                        return
