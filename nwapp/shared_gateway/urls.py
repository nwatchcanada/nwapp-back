from django.urls import path

from shared_gateway.views import *


urlpatterns = (
    path('api/v1/public/login', SharedLoginAPIView.as_view(), name='nwapp_shared_login_api_endpoint'),
    path('api/v1/public/logout', SharedLogoutAPIView.as_view(), name='nwapp_shared_logout_api_endpoint'),
    path('api/v1/public/profile', SharedProfileRetrieveUpdateAPIView.as_view(), name='nwapp_shared_profile_api_endpoint'),
    path('api/v1/public/refresh-token', SharedRefreshTokenAPIView.as_view(), name='nwapp_shared_refresh_token_api_endpoint'),
)
