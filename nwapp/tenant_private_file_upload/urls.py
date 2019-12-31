from django.urls import path

from tenant_private_file_upload import views


urlpatterns = (
    path('api/v1/private-file-uploads', views.PrivateFileUploadListCreateAPIView.as_view(), name='nwapp_private_file_upload_list_create_api_endpoint'),
    path('api/v1/private-file-upload/<int:id>', views.PrivateFileUploadRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_private_file_upload_retrieve_update_delete_api_endpoint'),
)
