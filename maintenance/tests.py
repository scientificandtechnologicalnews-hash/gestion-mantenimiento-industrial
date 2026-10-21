from django.contrib.auth.models import Group, User
from django.core.management import call_command
from rest_framework.test import APITestCase

from .models import Documento, Maquina

import json
import tempfile
from pathlib import Path

from django.test import TestCase


class ApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Se ejecuta una vez y prepara datos. Django usa una BD temporal
        # para los tests, así que no toca tus datos reales.
        call_command("crear_roles")
        cls.maquina = Maquina.objects.create(
            nombre="PLC de prueba", codigo="PLC-TST-001", categoria="CTL"
        )
        Documento.objects.create(
            titulo="Fallo de prueba", tipo="FP", maquina=cls.maquina, contenido="texto"
        )
        cls.tecnico = User.objects.create_user("tec", password="clave-segura-123")
        cls.tecnico.groups.add(Group.objects.get(name="Técnico"))
        cls.sin_rol = User.objects.create_user("sinrol", password="clave-segura-123")

    def test_maquinas_son_publicas(self):
        r = self.client.get("/api/maquinas/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)

    def test_documentos_exigen_sesion(self):
        r = self.client.get("/api/documentos/")
        self.assertEqual(r.status_code, 403)

    def test_usuario_sin_rol_no_ve_documentos(self):
        self.client.force_login(self.sin_rol)   # simula una sesión iniciada
        r = self.client.get("/api/documentos/")
        self.assertEqual(r.status_code, 403)

    def test_tecnico_ve_documentos(self):
        self.client.force_login(self.tecnico)
        r = self.client.get("/api/documentos/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)

    def test_busqueda_de_documentos(self):
        self.client.force_login(self.tecnico)
        r = self.client.get("/api/documentos/?q=inexistente")
        self.assertEqual(r.data["count"], 0)

    def test_api_es_de_solo_lectura(self):
        self.client.force_login(self.tecnico)
        r = self.client.post("/api/documentos/", {"titulo": "hack"})
        self.assertIn(r.status_code, (403, 405))   # rechazado de cualquier forma
        self.assertEqual(Documento.objects.count(), 1)

    def test_estadisticas_exigen_permiso(self):
        self.assertEqual(self.client.get("/api/estadisticas/").status_code, 403)
        self.client.force_login(self.tecnico)
        self.assertEqual(self.client.get("/api/estadisticas/").status_code, 200)


class ImportacionTests(TestCase):
    def test_importar_es_idempotente(self):
        datos = [{
            "titulo": "fp_material: Fallo X: PLC Test",
            "tipo": "Material FP",
            "contenido_extraido": "texto",
            "archivo": "",
            "fuente_url": "",
            "maquina": "PLC Test [PLC-SIE-001]",
        }]
        # Carpeta temporal que se borra sola al salir del bloque "with"
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "datos.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            call_command("importar_documentos", str(ruta))
            call_command("importar_documentos", str(ruta))  # segunda vez: no duplica

        self.assertEqual(Maquina.objects.count(), 1)
        self.assertEqual(Documento.objects.count(), 1)
        self.assertEqual(Documento.objects.get().tipo, "FP")

# Create your tests here.
