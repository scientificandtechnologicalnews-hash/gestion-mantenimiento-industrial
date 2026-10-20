from django.conf import settings
from django.db import models


class Maquina(models.Model):
    """Equipo físico de la planta: PLC, motor, robot, sensor..."""

    # TextChoices: lista cerrada de opciones válidas.
    # (valor guardado en BD, texto que ve el usuario)
    class Categoria(models.TextChoices):
        ACCIONAMIENTO = "ACC", "Accionamientos (motores, variadores)"
        CONTROL = "CTL", "Control (PLC)"
        SENSORIZACION = "SEN", "Sensorización y lectura"
        TRANSPORTE = "TRA", "Transporte y clasificación"
        ROBOTICA = "ROB", "Robótica y almacenes automáticos"
        NEUMATICA = "NEU", "Neumática y servicios"
        OTROS = "OTR", "Otros"

    nombre = models.CharField(max_length=120)
    # unique=True: no puede haber dos máquinas con el mismo código
    codigo = models.CharField(max_length=30, unique=True)
    categoria = models.CharField(
        max_length=3, choices=Categoria.choices, default=Categoria.OTROS
    )
    ubicacion = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField(blank=True)
    # En lugar de borrar una máquina retirada, la marcamos como inactiva
    activa = models.BooleanField(default=True)
    # auto_now_add: se rellena sola con la fecha de creación
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["codigo"]
        verbose_name = "máquina"
        verbose_name_plural = "máquinas"

    def __str__(self):
        # Así se verá en el admin y en los desplegables
        return f"{self.nombre} [{self.codigo}]"


class Documento(models.Model):
    """Conocimiento técnico asociado a una máquina."""

    class Tipo(models.TextChoices):
        FALLO = "FP", "Fallo y solución"
        MANUAL = "MT", "Manual técnico"
        ESQUEMA = "EE", "Esquema eléctrico"

    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=2, choices=Tipo.choices)
    # ForeignKey = relación "muchos a uno".
    # on_delete=CASCADE: si se borra la máquina, se borran sus documentos.
    # related_name: permite hacer maquina.documentos.all()
    maquina = models.ForeignKey(
        Maquina, on_delete=models.CASCADE, related_name="documentos"
    )
    contenido = models.TextField(help_text="Texto del documento (se usará para buscar).")
    # blank=True: el campo es opcional en los formularios
    archivo = models.FileField(upload_to="manuales/", blank=True)
    fuente_url = models.URLField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # auto_now: se actualiza sola cada vez que se guarda
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["maquina", "titulo"]

    def __str__(self):
        return self.titulo


class Incidencia(models.Model):
    """Avería registrada por un técnico sobre una máquina."""

    class Prioridad(models.TextChoices):
        BAJA = "B", "Baja"
        MEDIA = "M", "Media"
        ALTA = "A", "Alta"

    class Estado(models.TextChoices):
        ABIERTA = "AB", "Abierta"
        EN_CURSO = "EC", "En curso"
        RESUELTA = "RE", "Resuelta"

    # PROTECT: no deja borrar una máquina que tenga incidencias,
    # así el historial de averías nunca se pierde.
    maquina = models.ForeignKey(
        Maquina, on_delete=models.PROTECT, related_name="incidencias"
    )
    # Apuntamos al modelo de usuario con settings.AUTH_USER_MODEL (buena práctica).
    # SET_NULL: si se borra el usuario, la incidencia se conserva sin técnico.
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="incidencias",
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    prioridad = models.CharField(
        max_length=1, choices=Prioridad.choices, default=Prioridad.MEDIA
    )
    estado = models.CharField(
        max_length=2, choices=Estado.choices, default=Estado.ABIERTA
    )
    solucion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # null=True: en base de datos puede estar vacío hasta que se resuelva
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]  # el signo menos = las más recientes primero

    def __str__(self):
        return f"{self.titulo} ({self.maquina.codigo})"

# Create your models here.
