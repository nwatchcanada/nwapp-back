from django.urls import path

from tenant_member.views import *


urlpatterns = (
    path('api/v1/members', MemberListCreateAPIView.as_view(), name='nwapp_members_list_create_api_endpoint'),
    path('api/v1/members/operation/avatar', MemberAvatarCreateOrUpdateOperationAPIView.as_view(), name='nwapp_members_avatar_operation_api_endpoint'),
    path('api/v1/member-comments', MemberCommentListCreateAPIView.as_view(), name='nwapp_member_comment_list_create_api_endpoint'),
    path('api/v1/member-files', MemberFileUploadListCreateAPIView.as_view(), name='nwapp_member_file_upload_list_create_api_endpoint'),
    path('api/v1/member/<slug>', MemberRetrieveAPIView.as_view(), name='nwapp_members_retrieve_api_endpoint'),
    path('api/v1/member/<slug>/address', MemberAddressUpdateAPIView.as_view(), name='nwapp_members_address_update_api_endpoint'),
    path('api/v1/member/<slug>/contact', MemberContactUpdateAPIView.as_view(), name='nwapp_members_contact_update_api_endpoint'),
    path('api/v1/member/<slug>/metrics', MemberMetricUpdateAPIView.as_view(), name='nwapp_members_metric_update_api_endpoint'),
    # path('api/v1/member/<slug>/files', MemberFileUploadListCreateAPIView.as_view(), name='nwapp_member_file_upload_api_endpoint'),
    # url(r'^api/associates/operation/avatar$', AssociateAvatarCreateOrUpdateOperationCreateAPIView.as_view(), name='workery_associate_avatar_operation_api_endpoint'),
)
