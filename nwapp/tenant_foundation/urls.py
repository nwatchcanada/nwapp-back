from django.urls import path

from . import views


urlpatterns = (
    path('api/v1/tags', views.TagListCreateAPIView.as_view(), name='nwapp_tag_list_create_api_endpoint'),
    path('api/v1/tag/<int:pk>', views.TagRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_tag_retrieve_update_delete_api_endpoint'),
    path('api/v1/how-hears', views.HowHearAboutUsItemListCreateAPIView.as_view(), name='nwapp_how_did_you_hear_list_create_api_endpoint'),
    path('api/v1/how-hear/<int:pk>', views.HowHearAboutUsItemRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_how_did_you_hear_retrieve_update_delete_api_endpoint'),
    path('api/v1/expectations', views.ExpectationItemListCreateAPIView.as_view(), name='nwapp_expectation_item_list_create_api_endpoint'),
    path('api/v1/expectation/<int:id>', views.ExpectationItemRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_expectation_items_retrieve_update_delete_api_endpoint'),
    path('api/v1/meanings', views.MeaningItemListCreateAPIView.as_view(), name='nwapp_meaning_item_list_create_api_endpoint'),
    path('api/v1/meaning/<int:id>', views.MeaningItemRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_meaning_item_retrieve_update_delete_api_endpoint'),
    path('api/v1/score-points', views.ScorePointListCreateAPIView.as_view(), name='nwapp_score_point_list_create_api_endpoint'),
    path('api/v1/score-point/<uuid>', views.ScorePointRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_score_point_retrieve_update_delete_api_endpoint'),
    path('api/v1/badges', views.BadgeListCreateAPIView.as_view(), name='nwapp_badge_list_create_api_endpoint'),
    path('api/v1/badge/<uuid>', views.BadgeRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_badge_retrieve_update_delete_api_endpoint'),
    path('api/v1/awards', views.AwardListCreateAPIView.as_view(), name='nwapp_award_list_create_api_endpoint'),
    path('api/v1/award/<uuid>', views.AwardRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_award_retrieve_update_delete_api_endpoint'),
    path('api/v1/districts', views.DistrictListCreateAPIView.as_view(), name='nwapp_district_list_create_api_endpoint'),
    path('api/v1/district/<slug>', views.DistrictRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_district_retrieve_update_delete_api_endpoint'),
    path('api/v1/district/<slug>/operation/boundary', views.DistrictBoundaryOperationAPIView.as_view(), name='nwapp_district_boundary_operation_api_endpoint'),
    path('api/v1/announcements', views.AnnouncementListCreateAPIView.as_view(), name='nwapp_announcement_list_create_api_endpoint'),
    path('api/v1/announcement/<slug>', views.AnnouncementRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_announcement_retrieve_update_delete_api_endpoint'),
    path('api/v1/resource-items', views.ResourceItemListCreateAPIView.as_view(), name='nwapp_resource_item_list_create_api_endpoint'),
    path('api/v1/resource-item/<slug>', views.ResourceItemRetrieveUpdateDestroyAPIView.as_view(), name='nwapp_resource_item_retrieve_update_delete_api_endpoint'),
    path('api/v1/search', views.UnifiedSearchItemListAPIView.as_view(), name='nwapp_unified_search_list_api_endpoint'),
)
