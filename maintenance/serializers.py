from rest_framework import serializers

from .models import Documento, Incidencia, Maquina


class MaquinaSerializer(serializers.ModelSerializer):
    # get_categoria_display es un método que Django crea solo para los campos con choices.
    # Devuelve el texto legible ("Control (PLC)") en lugar del código ("CTL").
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = Maquina
        fields = ["id", "codigo", "nombre", "categoria", "categoria_display", "ubicacion"]


class DocumentoListSerializer(serializers.ModelSerializer):
    """Versión resumida, para listados."""

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    # source con punto: sigue la relación hasta el código de la máquina
    maquina_codigo = serializers.CharField(source="maquina.codigo", read_only=True)
    # SerializerMethodField: campo calculado por el método get_<nombre>
    extracto = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = ["id", "titulo", "tipo", "tipo_display", "maquina",
                  "maquina_codigo", "extracto", "fecha_actualizacion"]

    def get_extracto(self, obj):
        # Solo los primeros 200 caracteres: el listado no debe cargar textos enteros
        return obj.contenido[:200]


class DocumentoDetalleSerializer(serializers.ModelSerializer):
    """Versión completa, para ver un documento."""

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    maquina_codigo = serializers.CharField(source="maquina.codigo", read_only=True)

    class Meta:
        model = Documento
        fields = ["id", "titulo", "tipo", "tipo_display", "maquina", "maquina_codigo",
                  "contenido", "fuente_url", "fecha_creacion", "fecha_actualizacion"]


class IncidenciaSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    prioridad_display = serializers.CharField(source="get_prioridad_display", read_only=True)
    maquina_codigo = serializers.CharField(source="maquina.codigo", read_only=True)
    # allow_null: una incidencia puede quedarse sin técnico si se borra el usuario
    tecnico_username = serializers.CharField(
        source="tecnico.username", read_only=True, allow_null=True
    )

    class Meta:
        model = Incidencia
        fields = ["id", "maquina", "maquina_codigo", "titulo", "descripcion",
                  "prioridad", "prioridad_display", "estado", "estado_display",
                  "solucion", "tecnico_username", "fecha_creacion", "fecha_resolucion"]


        