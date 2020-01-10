from django.urls import path

from tenant_area_coordinator.views import *


urlpatterns = (
    path('api/v1/area-coordinators', AreaCoordinatorListCreateAPIView.as_view(), name='nwapp_area_coordinators_list_create_api_endpoint'),
    path('api/v1/area-coordinators/operation/avatar', AreaCoordinatorAvatarCreateOrUpdateOperationAPIView.as_view(), name='nwapp_area_coordinators_avatar_operation_api_endpoint'),
    path('api/v1/area-coordinators/operation/archive', AreaCoordinatorArchiveOperationAPIView.as_view(), name='nwapp_area_coordinators_archive_operation_api_endpoint'),
    path('api/v1/area-coordinators/operation/promote', AreaCoordinatorPromoteOperationAPIView.as_view(), name='nwapp_area_coordinators_promote_operation_api_endpoint'),
    path('api/v1/area-coordinators/operation/demote', AreaCoordinatorDemoteOperationAPIView.as_view(), name='nwapp_area_coordinators_demote_operation_api_endpoint'),
    path('api/v1/area-coordinator-comments', AreaCoordinatorCommentListCreateAPIView.as_view(), name='nwapp_area_coordinator_comment_list_create_api_endpoint'),
    path('api/v1/area-coordinator-files', AreaCoordinatorFileUploadListCreateAPIView.as_view(), name='nwapp_area_coordinator_file_upload_list_create_api_endpoint'),
    path('api/v1/area-coordinator/<slug>', AreaCoordinatorRetrieveAPIView.as_view(), name='nwapp_area_coordinators_retrieve_api_endpoint'),
    path('api/v1/area-coordinator/<slug>/address', AreaCoordinatorAddressUpdateAPIView.as_view(), name='nwapp_area_coordinators_address_update_api_endpoint'),
    path('api/v1/area-coordinator/<slug>/contact', AreaCoordinatorContactUpdateAPIView.as_view(), name='nwapp_area_coordinators_contact_update_api_endpoint'),
    path('api/v1/area-coordinator/<slug>/metrics', AreaCoordinatorMetricUpdateAPIView.as_view(), name='nwapp_area_coordinators_metric_update_api_endpoint'),
)
