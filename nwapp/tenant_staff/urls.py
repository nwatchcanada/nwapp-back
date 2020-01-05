from django.urls import path

from tenant_staff.views import *


urlpatterns = (
    path('api/v1/staffs', StaffListCreateAPIView.as_view(), name='nwapp_staffs_list_create_api_endpoint'),
    path('api/v1/staffs/operation/avatar', StaffAvatarCreateOrUpdateOperationAPIView.as_view(), name='nwapp_staffs_avatar_operation_api_endpoint'),
    path('api/v1/staffs/operation/archive', StaffArchiveOperationAPIView.as_view(), name='nwapp_staffs_archive_operation_api_endpoint'),
    path('api/v1/staffs/operation/promote', StaffPromoteOperationAPIView.as_view(), name='nwapp_staffs_promote_operation_api_endpoint'),
    path('api/v1/staff-comments', StaffCommentListCreateAPIView.as_view(), name='nwapp_staff_comment_list_create_api_endpoint'),
    path('api/v1/staff-files', StaffFileUploadListCreateAPIView.as_view(), name='nwapp_staff_file_upload_list_create_api_endpoint'),
    path('api/v1/staff/<slug>', StaffRetrieveAPIView.as_view(), name='nwapp_staffs_retrieve_api_endpoint'),
    path('api/v1/staff/<slug>/address', StaffAddressUpdateAPIView.as_view(), name='nwapp_staffs_address_update_api_endpoint'),
    path('api/v1/staff/<slug>/contact', StaffContactUpdateAPIView.as_view(), name='nwapp_staffs_contact_update_api_endpoint'),
    path('api/v1/staff/<slug>/metrics', StaffMetricUpdateAPIView.as_view(), name='nwapp_staffs_metric_update_api_endpoint'),
)
