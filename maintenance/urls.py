from django.urls import path

from . import views

# app_name crea un "espacio de nombres": permite escribir 'maintenance:home'
# sin que choque con rutas de otras apps.
app_name = "maintenance"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),
]