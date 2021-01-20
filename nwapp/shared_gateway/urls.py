from django.urls import path

from shared_gateway.views import *


urlpatterns = (
    path('api/v1/public/login', SharedLoginAPIView.as_view(), name='nwapp_shared_login_api_endpoint'),
    path('api/v1/public/logout', SharedLogoutAPIView.as_view(), name='nwapp_shared_logout_api_endpoint'),
    path('api/v1/public/profile', SharedProfileRetrieveUpdateAPIView.as_view(), name='nwapp_shared_profile_api_endpoint'),
    path('api/v1/public/refresh-token', SharedRefreshTokenAPIView.as_view(), name='nwapp_shared_refresh_token_api_endpoint'),
    path('api/v1/public/activate-email/<pr_access_code>/',
        user_activation_email_page,
        name='nwapp_activate_email'
    ),
    path('api/v1/public/reset-password-email/<pr_access_code>/',
        reset_password_email_page,
        name='nwapp_reset_password_email'
    ),
    path('api/v1/public/user-was-created-email/<pr_access_code>/',
        user_was_created_email_page,
        name='nwapp_user_was_created_email'
    ),
    path('api/v1/public/reset-password', ResetPasswordAPIView.as_view(), name='nwapp_reset_password_api_endpoint'),
    path('api/v1/public/send-password-reset', SendPasswordResetAPIView.as_view(), name='nwapp_send_password_reset_api_endpoint'),
)
