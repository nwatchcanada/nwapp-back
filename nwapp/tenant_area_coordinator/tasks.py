import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def process_area_coordinator_with_slug_func(schema_name, slug):
    call_command('process_area_coordinator_with_slug', schema_name, slug, verbosity=0)


@job
def geocode_area_coordinator_address_func(schema_name, slug):
    call_command('geocode_area_coordinator_address', schema_name, slug, verbosity=0)


@job
def geoip2_area_coordinator_audit_func(organization, area_coordinator):
    organization.activate_tenant()

    if area_coordinator.created_from:
        area_coordinator.created_from_position = get_point_from_ip(area_coordinator.created_from)
    if area_coordinator.last_modified_from:
        area_coordinator.last_modified_from_position = get_point_from_ip(area_coordinator.last_modified_from)
    area_coordinator.save()


@job
def geoip2_area_coordinator_address_audit_func(organization, area_coordinator_address):
    organization.activate_tenant()

    if area_coordinator_address.created_from:
        area_coordinator_address.created_from_position = get_point_from_ip(area_coordinator_address.created_from)
    if area_coordinator_address.last_modified_from:
        area_coordinator_address.last_modified_from_position = get_point_from_ip(area_coordinator_address.last_modified_from)
    area_coordinator_address.save()


@job
def geoip2_area_coordinator_contact_audit_func(organization, area_coordinator_contact):
    organization.activate_tenant()

    if area_coordinator_contact.created_from:
        area_coordinator_contact.created_from_position = get_point_from_ip(area_coordinator_contact.created_from)
    if area_coordinator_contact.last_modified_from:
        area_coordinator_contact.last_modified_from_position = get_point_from_ip(area_coordinator_contact.last_modified_from)
    area_coordinator_contact.save()


@job
def geoip2_area_coordinator_metric_audit_func(organization, area_coordinator_metric):
    organization.activate_tenant()

    if area_coordinator_metric.created_from:
        area_coordinator_metric.created_from_position = get_point_from_ip(area_coordinator_metric.created_from)
    if area_coordinator_metric.last_modified_from:
        area_coordinator_metric.last_modified_from_position = get_point_from_ip(area_coordinator_metric.last_modified_from)
    area_coordinator_metric.save()


@job
def geoip2_area_coordinator_comment_audit_func(organization, area_coordinator_comment):
    organization.activate_tenant()

    if area_coordinator_comment.comment:
        comment = area_coordinator_comment.comment
        if comment.created_from:
            comment.created_from_position = get_point_from_ip(comment.created_from)
        if comment.last_modified_from:
            comment.last_modified_from_position = get_point_from_ip(comment.last_modified_from)
        comment.save()
