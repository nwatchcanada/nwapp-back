from django.urls import path

from tenant_dashboard.views import *


urlpatterns = (
    path('api/v1/dashboard', DashboardAPI.as_view(), name='nwapp_dashboard_api_endpoint'),
)
