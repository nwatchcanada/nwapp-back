from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SharedFoundationConfig(AppConfig):
    name = 'shared_foundation'
    verbose_name = _('Shared Foundation')

    def ready(self):
        import shared_foundation.signals  # noqa
