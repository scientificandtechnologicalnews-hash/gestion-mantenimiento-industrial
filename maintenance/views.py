from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Maquina


def home(request):
    """Página pública: la ve cualquiera, incluso sin iniciar sesión (Visitante)."""
    total = Maquina.objects.filter(activa=True).count()
    return render(request, "home.html", {"total_maquinas": total})


# @login_required: si no hay sesión iniciada, Django redirige al login
@login_required
def panel(request):
    """Panel privado: solo para usuarios autenticados."""
    grupos = request.user.groups.values_list("name", flat=True)
    return render(request, "panel.html", {"grupos": grupos})

# Create your views here.
