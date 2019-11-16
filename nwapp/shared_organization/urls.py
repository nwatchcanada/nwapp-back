from django.urls import path

from .views import *


urlpatterns = (
    path('api/v1/public/organizations', SharedOrganizationListCreateAPIView.as_view(), name='nwapp_organization_list_create_api_endpoint'),
    path('api/v1/public/organization/<str:schema_name>', SharedOrganizationRetrieveUpdateDeleteAPIView.as_view(), name='nwapp_organization_retrieve_update_delete_api_endpoint'),
    # path('api/v1/logout', SharedLogoutAPIView.as_view(), name='nwapp_logout_api_endpoint'),
    # path('api/v1/profile', SharedProfileRetrieveUpdateAPIView.as_view(), name='nwapp_profile_api_endpoint'),
    # path('api/v1/refresh-token', SharedRefreshTokenAPIView.as_view(), name='nwapp_profile_api_endpoint'),
)
