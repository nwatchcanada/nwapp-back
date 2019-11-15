from django.urls import path

from shared_gateway.views import *


urlpatterns = (
    path('api/v1/login', SharedLoginAPIView.as_view(), name='nwapp_login_api_endpoint'),
    path('api/v1/logout', SharedLogoutAPIView.as_view(), name='nwapp_logout_api_endpoint'),
    path('api/v1/profile', SharedProfileRetrieveUpdateAPIView.as_view(), name='nwapp_profile_api_endpoint'),
    path('api/v1/refresh-token', SharedRefreshTokenAPIView.as_view(), name='nwapp_profile_api_endpoint'),
)
