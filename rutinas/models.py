from django.db import models
from django.conf import settings

#   Modelo ejercicios
CATEGORIAS_EJERCICIO = [
    ("Pecho", "Pecho"),
    ("Espalda", "Espalda"),
    ("Pierna", "Pierna"),
    ("Hombro", "Hombro"),
    ("Brazo", "Brazo"),
    ("Cardio", "Cardio"),
    ("Abdominal", "Abdominal"),
    ("Estiramiento", "Estiramiento"),
    # Puedes añadir más categorías aquí
]


class Ejercicios(models.Model):

    nombre = models.CharField(max_length=100, verbose_name="Nombre del Ejercicio")

    descripcion = models.TextField(verbose_name="Descripción o Instrucciones")

    # Columna 'categoria' como CharField con opciones restringidas
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_EJERCICIO,
        default="Pecho",
        verbose_name="Categoría Muscular",
    )

    video_url = models.URLField(
        max_length=200, blank=True, null=True, verbose_name="Enlace de Video (URL)"
    )

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"

    def __str__(self):
        return self.nombre


# Modelo DetalleEjercicio
class DetalleEjercicio(models.Model):
    # El campo 'id' es creado automáticamente por Django

    # Clave Foránea al modelo Ejercicio
    ejercicio = models.ForeignKey(
        "Ejercicios",  # Referencia al modelo Ejercicio
        on_delete=models.CASCADE,  # Si el ejercicio se borra, sus detalles también
        related_name="detalles",  # Para acceder a los detalles desde el ejercicio (ej: ejercicio.detalles.all())
        verbose_name="Ejercicio Asociado",
    )

    # Columna 'peso' (float)
    peso = models.FloatField(
        verbose_name="Peso (kg o lbs)", help_text="El peso utilizado para el ejercicio."
    )

    # Columna 'repeticiones' (int)
    repeticiones = models.IntegerField(verbose_name="Repeticiones")

    # Columna 'series' (int)
    series = models.IntegerField(verbose_name="Series")

    # Columna 'descanso' (int)
    descanso = models.IntegerField(
        verbose_name="Descanso (minutos)", help_text="Tiempo de descanso entre series."
    )

    class Meta:
        verbose_name = "Detalle de Ejercicio"
        verbose_name_plural = "Detalles de Ejercicios"

    def __str__(self):
        return f"Detalle de {self.ejercicio.nombre} - {self.series} series"


class Rutina(models.Model):

    nombre = models.CharField(max_length=100, verbose_name="Nombre de la rutina")

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rutinas",
        verbose_name="Usuario",
    )

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"

    def __str__(self):
        return self.nombre


from django.db import models

# Asumimos que Rutina y DetalleEjercicio están accesibles (misma app o importados)

# Opciones para el campo dia_semana
DIAS_SEMANA = [
    (1, "Lunes"),
    (2, "Martes"),
    (3, "Miércoles"),
    (4, "Jueves"),
    (5, "Viernes"),
    (6, "Sábado"),
    (7, "Domingo"),
]


class RutinaDia(models.Model):
    # ID (PK) es creado automáticamente

    # FK 1: Relaciona con la Rutina (ej. "Rutina de 4 días de Jorge")
    rutina = models.ForeignKey(
        "Rutina",
        on_delete=models.CASCADE,
        related_name="dias_rutina",
        verbose_name="Rutina Base",
    )

    # FK 2: Relaciona con la configuración específica del ejercicio
    # (ej. "Press banca: 3 series, 10 reps, 80kg")
    detalle_ejercicio = models.ForeignKey(
        "DetalleEjercicio",
        on_delete=models.CASCADE,
        related_name="rutinas_asociadas",
        verbose_name="Detalle del Ejercicio (Peso/Reps)",
    )

    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA, verbose_name="Día de la Semana"
    )

    orden = models.PositiveSmallIntegerField(
        default=0, verbose_name="Orden del Ejercicio en el Día"
    )

    class Meta:
        verbose_name = "Ejercicio Asignado por Día"
        verbose_name_plural = "Ejercicios Asignados por Día"
        unique_together = ("rutina", "detalle_ejercicio", "dia_semana")
        ordering = ["rutina", "dia_semana", "orden"]

    def __str__(self):
        return f"{self.get_dia_semana_display()} en {self.rutina.nombre}"
