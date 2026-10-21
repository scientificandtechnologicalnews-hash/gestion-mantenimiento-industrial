from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import IncidenciaCrearForm, IncidenciaEditarForm
from .models import Documento, Incidencia, Maquina

from django.conf import settings
from django.http import Http404, HttpResponse


def es_administrador(user):
    """True si el usuario es superusuario o pertenece al grupo Administrador."""
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


# ---------- Páginas generales ----------

def home(request):
    """Página pública: la ve cualquiera (Visitante)."""
    total = Maquina.objects.filter(activa=True).count()
    return render(request, "home.html", {"total_maquinas": total})



@login_required
def panel(request):
    """Panel privado: solo usuarios autenticados."""
    grupos = request.user.groups.values_list("name", flat=True)
    return render(request, "panel.html", {"grupos": grupos})


# ---------- Máquinas y documentos ----------

def maquina_lista(request):
    """Listado público con buscador, filtro por categoría y paginación."""
    maquinas = Maquina.objects.filter(activa=True)

    # request.GET contiene los parámetros de la URL (?q=plc&categoria=CTL)
    q = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")

    if q:
        # Q permite combinar condiciones con OR (|). icontains ignora mayúsculas.
        maquinas = maquinas.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if categoria:
        maquinas = maquinas.filter(categoria=categoria)

    # Paginación: 10 máquinas por página
    page = Paginator(maquinas, 10).get_page(request.GET.get("page"))

    return render(request, "maquinas/lista.html", {
        "page": page,
        "q": q,
        "categoria": categoria,
        "categorias": Maquina.Categoria.choices,
    })


@login_required
@permission_required("maintenance.view_documento", raise_exception=True)
def maquina_detalle(request, pk):
    """Ficha de una máquina con su base de conocimiento y sus últimas averías."""
    # get_object_or_404: si no existe, devuelve la página de error 404
    maquina = get_object_or_404(Maquina, pk=pk, activa=True)

    documentos = maquina.documentos.all()
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")

    if q:
        documentos = documentos.filter(Q(titulo__icontains=q) | Q(contenido__icontains=q))
    if tipo:
        documentos = documentos.filter(tipo=tipo)

    return render(request, "maquinas/detalle.html", {
        "maquina": maquina,
        "documentos": documentos,
        "incidencias": maquina.incidencias.all()[:5],  # solo las 5 más recientes
        "q": q,
        "tipo": tipo,
        "tipos": Documento.Tipo.choices,
    })


@login_required
@permission_required("maintenance.view_documento", raise_exception=True)
def documento_detalle(request, pk):
    documento = get_object_or_404(Documento.objects.select_related("maquina"), pk=pk)
    return render(request, "maquinas/documento.html", {"documento": documento})


# ---------- Incidencias ----------

@login_required
@permission_required("maintenance.view_incidencia", raise_exception=True)
def incidencia_lista(request):
    # select_related hace un JOIN y evita una consulta extra por cada fila
    incidencias = Incidencia.objects.select_related("maquina", "tecnico")

    estado = request.GET.get("estado", "")
    if estado:
        incidencias = incidencias.filter(estado=estado)

    incidencias = list(incidencias)
    admin = es_administrador(request.user)
    for i in incidencias:
        # Marcamos cuáles puede editar este usuario (lo usa la plantilla)
        i.editable = admin or i.tecnico_id == request.user.id

    return render(request, "incidencias/lista.html", {
        "incidencias": incidencias,
        "estado": estado,
        "estados": Incidencia.Estado.choices,
    })


@login_required
@permission_required("maintenance.add_incidencia", raise_exception=True)
def incidencia_crear(request):
    if request.method == "POST":
        form = IncidenciaCrearForm(request.POST)
        if form.is_valid():
            # commit=False: crea el objeto SIN guardarlo aún, para completarlo
            incidencia = form.save(commit=False)
            incidencia.tecnico = request.user   # lo asigna el servidor, no el formulario
            incidencia.save()
            messages.success(request, "Incidencia registrada correctamente.")
            return redirect("maintenance:incidencia_lista")
    else:
        # Si venimos desde la ficha de una máquina (?maquina=3), la preseleccionamos
        form = IncidenciaCrearForm(initial={"maquina": request.GET.get("maquina")})

    return render(request, "incidencias/form.html", {"form": form, "titulo": "Nueva incidencia"})


@login_required
@permission_required("maintenance.change_incidencia", raise_exception=True)
def incidencia_editar(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)

    # Autorización a nivel de objeto: solo el autor o un administrador
    if incidencia.tecnico_id != request.user.id and not es_administrador(request.user):
        raise PermissionDenied  # Django devuelve el error 403

    # instance=incidencia: el formulario edita ESTE registro en lugar de crear otro
    form = IncidenciaEditarForm(request.POST or None, instance=incidencia)
    if request.method == "POST" and form.is_valid():
        incidencia = form.save(commit=False)
        # Gestionamos la fecha de resolución según el estado
        if incidencia.estado == Incidencia.Estado.RESUELTA:
            if incidencia.fecha_resolucion is None:
                incidencia.fecha_resolucion = timezone.now()
        else:
            incidencia.fecha_resolucion = None
        incidencia.save()
        messages.success(request, "Incidencia actualizada.")
        return redirect("maintenance:incidencia_lista")

    return render(request, "incidencias/form.html", {"form": form, "titulo": "Editar incidencia"})


def app_react(request):
    """Entrega la página principal de React ya compilada.
    La página en sí es pública; los datos que pide a la API siguen protegidos por permisos."""
    index = settings.BASE_DIR / "frontend" / "dist" / "index.html"
    if not index.exists():
        raise Http404("React no está compilado: ejecuta 'npm run build' en la carpeta frontend.")
    return HttpResponse(index.read_text(encoding="utf-8"))

# Create your views here.
