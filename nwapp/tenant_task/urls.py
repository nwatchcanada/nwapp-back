from django.urls import path

from tenant_task.views import *


urlpatterns = (
    # path('api/v1/item-types', ItemTypeListCreateAPIView.as_view(), name='nwapp_item_types_list_create_api_endpoint'),
    # path('api/v1/item-type/<uuid>', ItemTypeRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_item_types_retrieve_update_delete_api_endpoint'),
    path('api/v1/task-items', TaskItemListAPIView.as_view(), name='nwapp_task_item_list_api_endpoint'),
    # path('api/v1/item-comments', ItemCommentListCreateAPIView.as_view(), name='nwapp_item_comment_list_create_api_endpoint'),
    path('api/v1/task-item/<uuid>', TaskItemRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_task_item_retrieve_update_destroy_api_endpoint'),
    # path('api/v1/item/<uuid>/update-category', ItemCategoryUpdateAPIView.as_view(), name='nwapp_item_category_update_api_endpoint'),
    # path('api/v1/item/<uuid>/update-authorities', ItemAuthoritiesUpdateAPIView.as_view(), name='nwapp_item_authorities_update_api_endpoint'),
    # path('api/v1/item/<uuid>/update-details', ItemDetailsUpdateAPIView.as_view(), name='nwapp_item_details_update_api_endpoint'),
    # path('api/v1/items/operation/archive', ItemArchiveOperationAPIView.as_view(), name='nwapp_item_archive_api_endpoint'),
)
