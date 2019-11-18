from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TenantFoundationConfig(AppConfig):
    name = 'tenant_foundation'
    verbose_name = _('Tenant Foundation')

    def ready(self):
        import tenant_foundation.signals  # noqa
