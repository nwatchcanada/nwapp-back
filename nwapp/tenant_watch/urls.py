from django.urls import path

from tenant_watch.views import *


urlpatterns = (
    path('api/v1/watches', WatchListCreateAPIView.as_view(), name='nwapp_watches_list_create_api_endpoint'),
    # path('api/v1/watchs/operation/avatar', WatchAvatarCreateOrUpdateOperationAPIView.as_view(), name='nwapp_watchs_avatar_operation_api_endpoint'),
    path('api/v1/watches/operation/archive', WatchArchiveOperationAPIView.as_view(), name='nwapp_watchse_archive_operation_api_endpoint'),
    # path('api/v1/watchs/operation/promote', WatchPromoteOperationAPIView.as_view(), name='nwapp_watchs_promote_operation_api_endpoint'),
    path('api/v1/watch-comments', WatchCommentListCreateAPIView.as_view(), name='nwapp_watch_comment_list_create_api_endpoint'),
    # path('api/v1/watch-files', WatchFileUploadListCreateAPIView.as_view(), name='nwapp_watch_file_upload_list_create_api_endpoint'),
    path('api/v1/watch/<slug>', WatchRetrieveDestroyAPIView.as_view(), name='nwapp_watchs_retrieve_api_endpoint'),
    path('api/v1/watch/<slug>/street', WatchStreetMembershipUpdateAPIView.as_view(), name='nwapp_watchs_street_update_api_endpoint'),
    path('api/v1/watch/<slug>/info', WatchInformationUpdateAPIView.as_view(), name='nwapp_watchs_info_update_api_endpoint'),
    # path('api/v1/watch/<slug>/metrics', WatchMetricUpdateAPIView.as_view(), name='nwapp_watchs_metric_update_api_endpoint'),
)
