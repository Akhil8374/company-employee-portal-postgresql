from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Employee Web Pages
    path("", include("employees.urls")),

    # Function-Based Views, APIViews, Generic Views, ViewSets
    path("api/", include("api.urls")),

    # JWT Authentication APIs
    path("api/auth/", include("api.auth_urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )