from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Documento, Incidencia, Maquina
from .permissions import PermisoVerModelo
from .serializers import (
    DocumentoDetalleSerializer,
    DocumentoListSerializer,
    IncidenciaSerializer,
    MaquinaSerializer,
)


# ReadOnlyModelViewSet: solo ofrece "listar" y "ver uno". No hay crear, editar ni borrar.
class MaquinaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado público de máquinas activas (igual que la página web pública)."""

    serializer_class = MaquinaSerializer
    permission_classes = [AllowAny]   # excepción explícita a la regla por defecto

    def get_queryset(self):
        qs = Maquina.objects.filter(activa=True)
        q = self.request.query_params.get("q", "").strip()
        categoria = self.request.query_params.get("categoria", "")
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
        if categoria:
            qs = qs.filter(categoria=categoria)
        return qs


class DocumentoViewSet(viewsets.ReadOnlyModelViewSet):
    """Documentos técnicos: requiere sesión y el permiso view_documento."""

    permission_classes = [PermisoVerModelo]
    # PermisoVerModelo necesita saber el modelo; lo deduce de este atributo
    queryset = Documento.objects.select_related("maquina")

    def get_serializer_class(self):
        # self.action vale "list" o "retrieve" según lo que se pida
        if self.action == "list":
            return DocumentoListSerializer
        return DocumentoDetalleSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(maquina__activa=True)
        params = self.request.query_params
        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(contenido__icontains=q))
        if params.get("tipo"):
            qs = qs.filter(tipo=params["tipo"])
        if params.get("maquina"):
            qs = qs.filter(maquina_id=params["maquina"])
        return qs


class IncidenciaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PermisoVerModelo]
    queryset = Incidencia.objects.select_related("maquina", "tecnico")
    serializer_class = IncidenciaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        for campo in ("estado", "prioridad", "maquina"):
            if params.get(campo):
                # Dos asteriscos: pasa {campo: valor} como argumento con nombre
                qs = qs.filter(**{campo: params[campo]})
        return qs


class EstadisticasView(APIView):
    """Indicadores para el panel de React. Es una vista a medida, no un ViewSet,
    porque no representa un modelo sino un resumen calculado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.has_perm("maintenance.view_incidencia"):
            raise PermissionDenied()

        # Cuántas incidencias hay en cada estado. order_by() vacío elimina la
        # ordenación del modelo, que interferiría con la agrupación.
        conteo = dict(
            Incidencia.objects.order_by().values_list("estado").annotate(total=Count("id"))
        )
        # Recorremos TODOS los estados posibles para que los que tienen 0 también salgan
        por_estado = [
            {"estado": valor, "etiqueta": texto, "total": conteo.get(valor, 0)}
            for valor, texto in Incidencia.Estado.choices
        ]

        # Las 5 máquinas con más averías
        top_maquinas = list(
            Maquina.objects.annotate(total=Count("incidencias"))
            .filter(total__gt=0)
            .order_by("-total", "codigo")
            .values("codigo", "nombre", "total")[:5]
        )

        # Tiempo medio de resolución: resta de fechas, promediada.
        # Es el indicador clave del problema que resolvemos (reducir paradas).
        duracion = ExpressionWrapper(
            F("fecha_resolucion") - F("fecha_creacion"), output_field=DurationField()
        )
        media = Incidencia.objects.filter(
            estado=Incidencia.Estado.RESUELTA, fecha_resolucion__isnull=False
        ).aggregate(media=Avg(duracion))["media"]
        horas_medias = round(media.total_seconds() / 3600, 1) if media else None

        return Response({
            "total_maquinas": Maquina.objects.filter(activa=True).count(),
            "total_documentos": Documento.objects.count(),
            "total_incidencias": Incidencia.objects.count(),
            "incidencias_por_estado": por_estado,
            "maquinas_con_mas_incidencias": top_maquinas,
            "horas_medias_resolucion": horas_medias,
        })

