from django.db import models
from django.conf import (
    settings,
)  # Usar settings.AUTH_USER_MODEL para referenciar al modelo User


class MedidaCorporal(models.Model):
    # Enlaza cada registro a un usuario. CASCADE borra las medidas si se borra el usuario.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medidas"
    )

    # Campo para la fecha y hora del registro (automático)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # Campos para las medidas (usando DecimalField para precisión con 0.1)
    pecho = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    brazo = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    brazo_der = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    antebrazo = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    antebrazo_der = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    cintura = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    pierna_izq = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    pierna_der = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    gemelos = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    gemelos_izq = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    cuello = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        # Ordenar por el más reciente primero por defecto
        ordering = ["-fecha_registro"]
        verbose_name = "Medida Corporal"
        verbose_name_plural = "Medidas Corporales"

    def __str__(self):
        return f"Medida de {self.usuario.username} en {self.fecha_registro.strftime('%Y-%m-%d')}"
