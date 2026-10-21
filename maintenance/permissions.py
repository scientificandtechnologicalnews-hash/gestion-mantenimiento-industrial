from rest_framework.permissions import DjangoModelPermissions


class PermisoVerModelo(DjangoModelPermissions):
    """Igual que DjangoModelPermissions, pero EXIGE también el permiso
    'view_' para leer (GET). Así un usuario sin rol no ve los datos."""

    perms_map = {
        **DjangoModelPermissions.perms_map,  # conserva las reglas de POST, PUT, DELETE...
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }

    