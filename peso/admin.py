from django.contrib import admin
from .models import RegistroPeso

@admin.register(RegistroPeso)
class RegistroPesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'peso', 'fecha_registro')
    list_filter = ('usuario', 'fecha_registro')
    ordering = ('-fecha_registro',)
