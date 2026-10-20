from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluye las rutas de login, logout, cambio de contraseña, etc.
    path("cuentas/", include("django.contrib.auth.urls")),
    # Rutas de nuestra app (la raíz del sitio)
    path("", include("maintenance.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)