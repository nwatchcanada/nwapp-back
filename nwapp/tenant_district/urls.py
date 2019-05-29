from django.urls import path

from tenant_district.views import *


urlpatterns = (
    path('api/districts',
        DistrictListCreateAPIView.as_view(),
        name='mikaponics_district_list_create_api_endpoint'
    ),
)
