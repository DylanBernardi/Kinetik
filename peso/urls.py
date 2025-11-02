from django.urls import path
from peso import views

urlpatterns = [
    path("registro_peso/", views.registro_peso, name="reg_peso"),
    path("registro_peso/guardar/", views.guardar_peso, name="guardar_peso"),
    path("registro_peso/obtener/", views.obtener_registros, name="obtener_registros"),
    path("registro_peso/eliminar/<int:registro_id>/", views.eliminar_registro, name="eliminar_registro"),
    path("registro_peso/generar_prueba/", views.generar_datos_prueba, name="generar_datos_prueba"),
]
