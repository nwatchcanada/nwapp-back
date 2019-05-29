from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SharedGroup(Group):
    """
    Class model is exactly the `Group` model with minor cosmetic change to
    make the naming convention consistent with our shared models.
    """

    class Meta:
        proxy = True # IMPORTANT
        app_label = 'shared_foundation'
        db_table = 'nwapp_shared_groups'
        verbose_name = _('Shared Group')
        verbose_name_plural = _('Shared Groups')
        default_permissions = ()
        permissions = ()
