from django.urls import path

from . import views


urlpatterns = (
    path('api/v1/tags', views.TagListCreateAPIView.as_view(), name='nwapp_tag_list_create_api_endpoint'),
    path('api/v1/tag/<int:id>', views.TagRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_tag_retrieve_update_delete_api_endpoint'),
)
