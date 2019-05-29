from django.urls import path

from shared_foundation import views


urlpatterns = (
    path('',
        views.index_view,
        name='nwapp_index_view'
    ),
)
