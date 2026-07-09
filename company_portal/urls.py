from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Employee App
    path("", include("employees.urls")),

    # Main API
    path("api/", include("api.urls.v1")),

    # Document Management APIs (Module 2)
    path("api/v1/documents/", include("documents.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )