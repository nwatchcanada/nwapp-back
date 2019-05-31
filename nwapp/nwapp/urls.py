
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include # This needs to be added

urlpatterns = ([
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('django-rq/', include('django_rq.urls')),
    # path('oauth/', include('social_django.urls', namespace='social')),

    # Allow the following apps for being accessed without language string.
    path('', include('shared_foundation.urls')),
    path('', include('shared_account.urls')),
    # path('', include('tenant_district.urls')),
    # path('', include('tenant_staff.urls')),
    path('', include('api.urls')),
])

# Add support for language specific context URLs.
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('shared_foundation.urls')),
    path('', include('shared_account.urls')),
    # path('', include('tenant_district.urls')),
    # path('', include('tenant_staff.urls')),
    path('', include('api.urls')),
    prefix_default_language=True
)
