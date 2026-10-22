from django.urls import path, include

urlpatterns = [

    # =====================================
    # API Version 1
    # Base: /api/v1/
    # =====================================
    path("v1/", include("config.api.v1.urls")),

    # =====================================
    # API Version 2 (Future)
    # Base: /api/v2/
    # =====================================
    path("v2/", include("config.api.v2.urls")),

]
