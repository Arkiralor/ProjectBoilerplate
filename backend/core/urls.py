from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenBlacklistView

from core import logger

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/admin/', include('admin_app.endpoints')),
    path('api/jobs/', include('job_handler_app.endpoints')),
    path('api/post/', include('post_app.endpoints')),
    path('api/user/', include('user_app.endpoints')),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),

    path('django-rq/', include('django_rq.urls')),
]

if settings.DEBUG and settings.ENV_TYPE.lower() == 'dev':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]


logger.info(f"Running in {settings.ENV_TYPE.upper()} mode with DEBUG: {settings.DEBUG}")