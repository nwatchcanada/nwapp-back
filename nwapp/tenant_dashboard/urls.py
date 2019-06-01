from django.conf.urls import include, url
from django.views.generic.base import RedirectView

from tenant_dashboard.views import *


urlpatterns = (
    ############################################################################
    url(r'^api/dashboard$',
        DashboardAPIView.as_view(),
        name='nwapp_dashboard_api_endpoint'
    ),
)
