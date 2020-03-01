from django.urls import path

from tenant_item.views import *


urlpatterns = (
    path('api/v1/item-types', ItemTypeListCreateAPIView.as_view(), name='nwapp_item_types_list_create_api_endpoint'),
    path('api/v1/item-type/<slug>', ItemTypeRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_item_types_retrieve_update_delete_api_endpoint'),
    path('api/v1/items', ItemListCreateAPIView.as_view(), name='nwapp_item_list_create_api_endpoint'),
    path('api/v1/item/<slug>', ItemRetrieveAPIView.as_view(), name='nwapp_item_retrieve_api_endpoint'),
    path('api/v1/item/<slug>/update-category', ItemCategoryUpdateAPIView.as_view(), name='nwapp_item_category_update_api_endpoint'),
    path('api/v1/item/<slug>/update-authorities', ItemAuthoritiesUpdateAPIView.as_view(), name='nwapp_item_authorities_update_api_endpoint'),
    path('api/v1/item/<slug>/update-details', ItemDetailsUpdateAPIView.as_view(), name='nwapp_item_details_update_api_endpoint'),
)
