# -*- coding: utf-8 -*-
import base64
import hashlib
import string
import math
import re # Regex
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.signing import Signer
from django.core.validators import RegexValidator
from django.db.models import Q
from django.urls import reverse
from django.utils import crypto
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants


def reverse_with_full_domain(reverse_url_id, resolve_url_args=[]):
    url = settings.NWAPP_BACKEND_HTTP_PROTOCOL
    url += settings.NWAPP_BACKEND_HTTP_DOMAIN
    url += reverse(reverse_url_id, args=resolve_url_args)
    url = url.replace("None","en")
    return url
