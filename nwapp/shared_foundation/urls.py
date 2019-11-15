from django.urls import path

from shared_foundation import views


urlpatterns = (
    path('', views.get_version_api),
    path('api', views.get_version_api),
    path('api/v1', views.get_version_api),
    path('api/v1/version', views.get_version_api),
)
