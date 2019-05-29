from django.urls import path

from tenant_district.views import *
from tenant_staff.views import *


urlpatterns = (
    # Districts
    path('api/districts', DistrictListCreateAPIView.as_view(), name='mikaponics_district_list_create_api_endpoint'),

    # Staff
    path('api/staff', StaffListAPIView.as_view(), name='mikaponics_staff_list_create_api_endpoint'),
)
