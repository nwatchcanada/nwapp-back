from django.urls import path

from tenant_district.views import *


urlpatterns = (
    path('api/districts',
        DistrictListAPIView.as_view(),
        name='mikaponics_crop_life_cycle_stage_list_api_endpoint'
    ),
)
