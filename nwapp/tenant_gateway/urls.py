from django.urls import path

from tenant_gateway.views import *


urlpatterns = (
    path('api/v1/login', TenantLoginAPIView.as_view(), name='nwapp_tenant_login_api_endpoint'),
    path('api/v1/logout', TenantLogoutAPIView.as_view(), name='nwapp_tenant_logout_api_endpoint'),
    path('api/v1/profile', TenantProfileRetrieveUpdateAPIView.as_view(), name='nwapp_tenant_profile_api_endpoint'),
    path('api/v1/refresh-token', TenantRefreshTokenAPIView.as_view(), name='nwapp_tenant_profile_api_endpoint'),
)
