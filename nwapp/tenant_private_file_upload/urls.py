from django.urls import path

from . import views


urlpatterns = (
    path('api/v1/private-file-uploads', views.PrivateFileUploadListCreateAPIView.as_view(), name='nwapp_private_file_upload_list_create_api_endpoint'),
    # path('api/v1/private-file/<int:id>', views.TagRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_tag_retrieve_update_delete_api_endpoint'),
)
