# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command


def run_send_activation_email_func(email):
    call_command('send_activation_email', email, verbosity=0)


def run_send_reset_password_email_func(email):
    call_command('send_reset_password_email', email, verbosity=0)


def run_send_user_was_created_to_staff_email_func(email):
    call_command('send_user_was_created_to_staff_email', email, verbosity=0)
