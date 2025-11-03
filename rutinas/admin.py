from django.contrib import admin
from .models import Rutina,RutinaDia,DetalleEjercicio,Ejercicios

admin.site.register(RutinaDia)
admin.site.register(Rutina)
admin.site.register(DetalleEjercicio)
admin.site.register(Ejercicios)