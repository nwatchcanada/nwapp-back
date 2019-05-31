from django.urls import path

from shared_account.views import *


urlpatterns = (
    path('api/login', SharedLoginAPIView.as_view(), name='nwapp_login_api_endpoint'),
    path('api/logout', SharedLogoutAPIView.as_view(), name='nwapp_logout_api_endpoint'),
    path('api/profile', SharedProfileRetrieveUpdateAPIView.as_view(), name='nwapp_profile_api_endpoint'),
)
