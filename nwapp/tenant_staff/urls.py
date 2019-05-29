from django.urls import path

from tenant_staff.views import *


urlpatterns = (
    path('api/staff',
        StaffListAPIView.as_view(),
        name='mikaponics_staff_list_create_api_endpoint'
    ),
)
