from django.urls import path

from . import views


app_name = "maintenance"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),

    path("maquinas/", views.maquina_lista, name="maquina_lista"),
    # <int:pk> captura el id de la URL y se lo pasa a la vista (pk = primary key)
    path("maquinas/<int:pk>/", views.maquina_detalle, name="maquina_detalle"),
    path("documentos/<int:pk>/", views.documento_detalle, name="documento_detalle"),

    path("incidencias/", views.incidencia_lista, name="incidencia_lista"),
    path("incidencias/nueva/", views.incidencia_crear, name="incidencia_crear"),
    path("incidencias/<int:pk>/editar/", views.incidencia_editar, name="incidencia_editar"),

    path("app/", views.app_react, name="app"),
]