from django.urls import path

from tenant_item.views import *


urlpatterns = (
    path('api/v1/item-types', ItemTypeListCreateAPIView.as_view(), name='nwapp_item_types_list_create_api_endpoint'),
    path('api/v1/item-type/<slug>', ItemTypeRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_item_types_retrieve_update_delete_api_endpoint'),
)
