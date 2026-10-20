from django.contrib import admin

from .models import Documento, Incidencia, Maquina


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "ubicacion", "activa")  # columnas de la lista
    list_filter = ("categoria", "activa")                                    # filtros laterales
    search_fields = ("codigo", "nombre")                                     # buscador


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "maquina", "fecha_actualizacion")
    list_filter = ("tipo", "maquina")
    search_fields = ("titulo", "contenido")


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "maquina", "tecnico", "prioridad", "estado", "fecha_creacion")
    list_filter = ("estado", "prioridad")
    search_fields = ("titulo", "descripcion")

# Register your models here.
