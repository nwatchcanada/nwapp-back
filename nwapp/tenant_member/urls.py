from django.urls import path

from tenant_member.views import *


urlpatterns = (
    path('api/v1/members', MemberListCreateAPIView.as_view(), name='nwapp_members_list_create_api_endpoint'),
)
