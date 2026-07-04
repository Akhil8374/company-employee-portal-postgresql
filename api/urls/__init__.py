from django.urls import path, include

urlpatterns = [
    # API Version 1
    path("v1/", include("api.urls.v1", namespace="v1")),

    # API Version 2
    path("v2/", include("api.urls.v2", namespace="v2")),
]
