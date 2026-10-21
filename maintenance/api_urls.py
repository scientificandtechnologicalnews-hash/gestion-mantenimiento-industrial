from django.urls import path
from rest_framework.routers import DefaultRouter

from .api_views import (
    DocumentoViewSet,
    EstadisticasView,
    IncidenciaViewSet,
    MaquinaViewSet,
)

# El router genera solo las rutas: /maquinas/ y /maquinas/<id>/, etc.
router = DefaultRouter()
router.register("maquinas", MaquinaViewSet, basename="api-maquina")
router.register("documentos", DocumentoViewSet, basename="api-documento")
router.register("incidencias", IncidenciaViewSet, basename="api-incidencia")

urlpatterns = [
    path("estadisticas/", EstadisticasView.as_view(), name="api-estadisticas"),
    *router.urls,   # el asterisco "desempaqueta" la lista de rutas del router
]

