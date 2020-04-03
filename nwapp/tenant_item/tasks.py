import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def geoip2_item_audit_func(organization, item):
    organization.activate_tenant()

    if item.created_from:
        item.created_from_position = get_point_from_ip(item.created_from)
    if item.last_modified_from:
        item.last_modified_from_position = get_point_from_ip(item.last_modified_from)
    item.save()
