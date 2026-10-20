from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea los grupos Administrador y Técnico con sus permisos"

    def handle(self, *args, **options):
        # get_or_create: si el grupo ya existe lo reutiliza, así el comando
        # se puede ejecutar varias veces sin duplicar nada.
        administrador, _ = Group.objects.get_or_create(name="Administrador")
        tecnico, _ = Group.objects.get_or_create(name="Técnico")

        # Django genera automáticamente 4 permisos por modelo:
        # add_, change_, delete_ y view_ (por ejemplo add_incidencia).
        permisos_app = Permission.objects.filter(content_type__app_label="maintenance")

        # El administrador recibe TODOS los permisos de la app.
        administrador.permissions.set(permisos_app)

        # El técnico solo recibe estos (principio de mínimo privilegio).
        permisos_tecnico = [
            "view_maquina",
            "view_documento",
            "view_incidencia",
            "add_incidencia",
            "change_incidencia",
        ]
        tecnico.permissions.set(permisos_app.filter(codename__in=permisos_tecnico))

        self.stdout.write(self.style.SUCCESS("Grupos y permisos creados correctamente."))