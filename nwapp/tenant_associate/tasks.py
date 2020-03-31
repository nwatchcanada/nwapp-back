import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.models import SharedOrganization
from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def process_associate_with_slug_func(schema_name, slug):
    call_command('process_associate_with_slug', schema_name, slug, verbosity=0)


@job
def geocode_associate_address_func(schema_name, associate_slug):
    call_command('geocode_associate_address', schema_name, associate_slug, verbosity=0)


@job
def geoip2_associate_audit_func(organization, associate):
    organization.activate_tenant()

    if associate.created_from:
        associate.created_from_position = get_point_from_ip(associate.created_from)
    if associate.last_modified_from:
        associate.last_modified_from_position = get_point_from_ip(associate.last_modified_from)
    associate.save()


@job
def geoip2_associate_address_audit_func(organization, associate_address):
    organization.activate_tenant()

    if associate_address.created_from:
        associate_address.created_from_position = get_point_from_ip(associate_address.created_from)
    if associate_address.last_modified_from:
        associate_address.last_modified_from_position = get_point_from_ip(associate_address.last_modified_from)
    associate_address.save()


@job
def geoip2_associate_contact_audit_func(organization, associate_contact):
    organization.activate_tenant()

    if associate_contact.created_from:
        associate_contact.created_from_position = get_point_from_ip(associate_contact.created_from)
    if associate_contact.last_modified_from:
        associate_contact.last_modified_from_position = get_point_from_ip(associate_contact.last_modified_from)
    associate_contact.save()


@job
def geoip2_associate_metric_audit_func(organization, associate_metric):
    organization.activate_tenant()

    if associate_metric.created_from:
        associate_metric.created_from_position = get_point_from_ip(associate_metric.created_from)
    if associate_metric.last_modified_from:
        associate_metric.last_modified_from_position = get_point_from_ip(associate_metric.last_modified_from)
    associate_metric.save()


@job
def geoip2_associate_comment_audit_func(organization, associate_comment):
    organization.activate_tenant()

    if associate_comment.comment:
        comment = associate_comment.comment
        if comment.created_from:
            comment.created_from_position = get_point_from_ip(comment.created_from)
        if comment.last_modified_from:
            comment.last_modified_from_position = get_point_from_ip(comment.last_modified_from)
        comment.save()
