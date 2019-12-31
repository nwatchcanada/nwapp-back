from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SharedGroup(Group):
    """
    Class model is exactly the `Group` model with minor cosmetic change to
    make the naming convention consistent with our shared models.
    """

    '''
    Constants & Choices
    '''

    class GROUP_MEMBERSHIP:
        EXECUTIVE = 1
        MANAGER = 2
        FRONTLINE_STAFF = 3
        ASSOCIATE = 4
        AREA_COORDINATOR = 5
        MEMBER = 6
        NONE = 0

    GROUP_MEMBERSHIP_CHOICES = (
        (GROUP_MEMBERSHIP.EXECUTIVE, _('Executive')),
        (GROUP_MEMBERSHIP.MANAGER, _('Manager')),
        (GROUP_MEMBERSHIP.FRONTLINE_STAFF, _('Frontline Staff')),
        (GROUP_MEMBERSHIP.ASSOCIATE, _('Associate')),
        (GROUP_MEMBERSHIP.AREA_COORDINATOR, _('Area Coordinator')),
        (GROUP_MEMBERSHIP.MEMBER, _('Member')),
        (GROUP_MEMBERSHIP.NONE, _('None')),
    )

    '''
    Metadata
    '''

    class Meta:
        proxy = True # IMPORTANT
        app_label = 'shared_foundation'
        db_table = 'nwapp_shared_groups'
        verbose_name = _('Shared Group')
        verbose_name_plural = _('Shared Groups')
        default_permissions = ()
        permissions = ()
