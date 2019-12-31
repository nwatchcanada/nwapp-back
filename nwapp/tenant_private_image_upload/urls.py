from django.urls import path

from tenant_private_image_upload import views


urlpatterns = (
    path('api/v1/private-image-uploads', views.PrivateImageUploadListCreateAPIView.as_view(), name='nwapp_private_image_upload_list_create_api_endpoint'),
    path('api/v1/private-image-upload/<slug>', views.PrivateImageUploadRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_private_image_upload_retrieve_update_delete_api_endpoint'),
)
