from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class RegistroPeso(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registros_peso",
        verbose_name=_("Usuario"),
    )

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Peso registrado en kilogramos.",
        verbose_name=_("Peso (kg)"),
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Fecha de Registro")
    )

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = _("Registro de Peso")
        verbose_name_plural = _("Registros de Peso")

    def __str__(self):
        return f'{self.usuario.username} - {self.peso} kg el {self.fecha_registro.strftime("%d/%m/%Y")}'
