from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from presentation import views as presentation 

handler404 = "presentation.views.error_404"
handler500 = "presentation.views.error_500"

urlpatterns = [
    path("", include("presentation.urls")),
    path("qr/", include("catalog.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("auth/", include("accounts.urls")),
    path('admin/tecof/icons/', presentation.icons_gallery_page, name='icons_gallery'),
    path("admin/", admin.site.urls),
    path("game/", include("game.urls")),   
    # path("api/", include("config.apis")),
    path("api/", include("config.api.urls")),   
       
]

# این کد فقط در حالت DEBUG=True کار می‌کند
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/assets/', document_root=settings.BASE_DIR / 'assets')