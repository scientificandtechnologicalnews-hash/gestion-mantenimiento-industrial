from django import forms

from .models import Incidencia, Maquina


class IncidenciaCrearForm(forms.ModelForm):
    """Formulario para registrar una avería nueva.
    OJO: no incluye 'tecnico' ni 'estado'; los pone el servidor."""

    class Meta:
        model = Incidencia
        fields = ["maquina", "titulo", "descripcion", "prioridad"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se pueden registrar incidencias sobre máquinas activas
        self.fields["maquina"].queryset = Maquina.objects.filter(activa=True)


class IncidenciaEditarForm(forms.ModelForm):
    """Formulario para actualizar el estado y la solución."""

    class Meta:
        model = Incidencia
        fields = ["titulo", "descripcion", "prioridad", "estado", "solucion"]

    def clean(self):
        # clean() valida varios campos a la vez.
        datos = super().clean()
        if datos.get("estado") == Incidencia.Estado.RESUELTA and not datos.get("solucion"):
            # Regla de negocio: no se puede cerrar una avería sin explicar la solución
            self.add_error("solucion", "Indica la solución para marcar la incidencia como resuelta.")
        return datos