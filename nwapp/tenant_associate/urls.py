from django.urls import path

from tenant_associate.views import *


urlpatterns = (
    path('api/v1/associates', AssociateListCreateAPIView.as_view(), name='nwapp_associates_list_create_api_endpoint'),
    path('api/v1/associates/operation/avatar', AssociateAvatarCreateOrUpdateOperationAPIView.as_view(), name='nwapp_associates_avatar_operation_api_endpoint'),
    path('api/v1/associates/operation/archive', AssociateArchiveOperationAPIView.as_view(), name='nwapp_associates_archive_operation_api_endpoint'),
    path('api/v1/associates/operation/promote', AssociatePromoteOperationAPIView.as_view(), name='nwapp_associates_promote_operation_api_endpoint'),
    path('api/v1/associate-comments', AssociateCommentListCreateAPIView.as_view(), name='nwapp_associate_comment_list_create_api_endpoint'),
    path('api/v1/associate-files', AssociateFileUploadListCreateAPIView.as_view(), name='nwapp_associate_file_upload_list_create_api_endpoint'),
    path('api/v1/associate/<slug>', AssociateRetrieveAPIView.as_view(), name='nwapp_associates_retrieve_api_endpoint'),
    path('api/v1/associate/<slug>/address', AssociateAddressUpdateAPIView.as_view(), name='nwapp_associates_address_update_api_endpoint'),
    path('api/v1/associate/<slug>/contact', AssociateContactUpdateAPIView.as_view(), name='nwapp_associates_contact_update_api_endpoint'),
    path('api/v1/associate/<slug>/metrics', AssociateMetricUpdateAPIView.as_view(), name='nwapp_associates_metric_update_api_endpoint'),
)
