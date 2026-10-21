import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from maintenance.models import Documento, Maquina

# El JSON trae el tipo como texto; el modelo guarda un código de 2 letras
TIPOS = {
    "Material FP": "FP",
    "Manual Técnico": "MT",
    "Esquema Eléctrico": "EE",
}

# Categoría de cada máquina según su código
CATEGORIAS = {
    "COM-ATL-001": "NEU",
    "VIS-KEY-001": "SEN",
    "PUE-HOR-001": "OTR",
    "PICK-AUT-001": "ROB",
    "VAR-SIE-001": "ACC",
    "MOT-SEW-001": "ACC",
    "SEN-OMR-002": "SEN",
    "SEN-SIC-001": "SEN",
    "LEC-ZEB-002": "SEN",
    "LEC-COG-001": "SEN",
    "PLC-SIE-002": "CTL",
    "PLC-SIE-001": "CTL",
    "ASR-SSI-001": "ROB",
    "ELV-SSI-001": "TRA",
    "SORT-VAN-001": "TRA",
    "CON-DEM-002": "TRA",
    "CON-INT-001": "TRA",
    "AMR-MIR-002": "ROB",
    "AMR-MIR-001": "ROB",
    "ROB-KUK-002": "ROB",
}


class Command(BaseCommand):
    help = "Importa máquinas y documentos técnicos desde un JSON"

    def add_arguments(self, parser):
        # nargs="?" hace el argumento opcional; si falta, usa la ruta por defecto
        parser.add_argument("ruta", nargs="?", default="data/documentos_rag.json")

    def handle(self, *args, **options):
        ruta = Path(options["ruta"])
        if not ruta.exists():
            raise CommandError(f"No existe el archivo: {ruta}")

        datos = json.loads(ruta.read_text(encoding="utf-8"))
        contadores = {"maq_nuevas": 0, "doc_nuevos": 0, "doc_actualizados": 0}

        # atomic: o se importa todo o no se importa nada.
        # Si algo falla a mitad, la base de datos queda como estaba.
        with transaction.atomic():
            for d in datos:
                # Separa "Compresor instalación neumática [COM-ATL-001]"
                coincide = re.match(r"^(.*)\s\[([^\]]+)\]\s*$", d["maquina"])
                if not coincide:
                    raise CommandError(f"Formato de máquina no válido: {d['maquina']}")
                nombre, codigo = coincide.groups()

                tipo = TIPOS.get(d["tipo"])
                if tipo is None:
                    raise CommandError(f"Tipo desconocido '{d['tipo']}' en: {d['titulo']}")

                # get_or_create: busca la máquina por código y, si no existe, la crea
                maquina, creada = Maquina.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        "nombre": nombre,
                        "categoria": CATEGORIAS.get(codigo, "OTR"),
                    },
                )
                contadores["maq_nuevas"] += creada

                # update_or_create: si el documento ya existe lo actualiza;
                # así el comando se puede repetir sin duplicar nada.
                _, creado = Documento.objects.update_or_create(
                    maquina=maquina,
                    titulo=d["titulo"],
                    defaults={
                        "tipo": tipo,
                        "contenido": d["contenido_extraido"],
                        "fuente_url": d.get("fuente_url", ""),
                    },
                )
                if creado:
                    contadores["doc_nuevos"] += 1
                else:
                    contadores["doc_actualizados"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Máquinas creadas: {contadores['maq_nuevas']} | "
            f"Documentos creados: {contadores['doc_nuevos']} | "
            f"Documentos actualizados: {contadores['doc_actualizados']}"
        ))
        