import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def geocode_member_address_func(schema_name, member_slug):
    call_command('geocode_member_address', schema_name, member_slug, verbosity=0)


@job
def geoip2_member_audit_func(schema_name, member_slug):
    call_command('geoip2_member_audit', schema_name, member_slug, verbosity=0)


@job
def geoip2_member_audit_func(organization, member):
    organization.activate_tenant()

    if member.created_from:
        member.created_from_position = get_point_from_ip(member.created_from)
    if member.last_modified_from:
        member.last_modified_from_position = get_point_from_ip(member.last_modified_from)
    member.save()
    

@job
def geoip2_member_address_audit_func(organization, member_address):
    organization.activate_tenant()

    if member_address.created_from:
        member_address.created_from_position = get_point_from_ip(member_address.created_from)
    if member_address.last_modified_from:
        member_address.last_modified_from_position = get_point_from_ip(member_address.last_modified_from)
    member_address.save()


@job
def geoip2_member_contact_audit_func(organization, member_contact):
    organization.activate_tenant()

    if member_contact.created_from:
        member_contact.created_from_position = get_point_from_ip(member_contact.created_from)
    if member_contact.last_modified_from:
        member_contact.last_modified_from_position = get_point_from_ip(member_contact.last_modified_from)
    member_contact.save()


@job
def geoip2_member_metric_audit_func(organization, member_metric):
    organization.activate_tenant()

    if member_metric.created_from:
        member_metric.created_from_position = get_point_from_ip(member_metric.created_from)
    if member_metric.last_modified_from:
        member_metric.last_modified_from_position = get_point_from_ip(member_metric.last_modified_from)
    member_metric.save()
