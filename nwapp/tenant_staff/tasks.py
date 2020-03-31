import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def process_staff_with_slug_func(schema_name, slug):
    call_command('process_staff_with_slug', schema_name, slug, verbosity=0)


@job
def geocode_staff_address_func(schema_name, staff_slug):
    call_command('geocode_staff_address', schema_name, staff_slug, verbosity=0)


@job
def geoip2_staff_audit_func(organization, staff):
    organization.activate_tenant()

    if staff.created_from:
        staff.created_from_position = get_point_from_ip(staff.created_from)
    if staff.last_modified_from:
        staff.last_modified_from_position = get_point_from_ip(staff.last_modified_from)
    staff.save()


@job
def geoip2_staff_address_audit_func(organization, staff_address):
    organization.activate_tenant()

    if staff_address.created_from:
        staff_address.created_from_position = get_point_from_ip(staff_address.created_from)
    if staff_address.last_modified_from:
        staff_address.last_modified_from_position = get_point_from_ip(staff_address.last_modified_from)
    staff_address.save()


@job
def geoip2_staff_contact_audit_func(organization, staff_contact):
    organization.activate_tenant()

    if staff_contact.created_from:
        staff_contact.created_from_position = get_point_from_ip(staff_contact.created_from)
    if staff_contact.last_modified_from:
        staff_contact.last_modified_from_position = get_point_from_ip(staff_contact.last_modified_from)
    staff_contact.save()


@job
def geoip2_staff_metric_audit_func(organization, staff_metric):
    organization.activate_tenant()

    if staff_metric.created_from:
        staff_metric.created_from_position = get_point_from_ip(staff_metric.created_from)
    if staff_metric.last_modified_from:
        staff_metric.last_modified_from_position = get_point_from_ip(staff_metric.last_modified_from)
    staff_metric.save()


@job
def geoip2_staff_comment_audit_func(organization, staff_comment):
    organization.activate_tenant()

    if staff_comment.comment:
        comment = staff_comment.comment
        if comment.created_from:
            comment.created_from_position = get_point_from_ip(comment.created_from)
        if comment.last_modified_from:
            comment.last_modified_from_position = get_point_from_ip(comment.last_modified_from)
        comment.save()
