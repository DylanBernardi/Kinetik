from django.contrib import admin
from django.urls import path
from rutinas import views

urlpatterns = [
    path("mis_rutinas/", views.mis_rutinas, name="mis_rutinas"),
    path("rutina/<int:rutina_id>/", views.mostrar_rutina, name="mostrar_rutina"),
    path(
        "eliminar_rutina/<int:rutina_id>/",
        views.eliminar_rutina,
        name="eliminar_rutina",
    ),
    path("crear_rutina/", views.crear_rutina, name="crear_rutina"),
    path("editar_rutina/<int:rutina_id>/", views.editar_rutina, name="editar_rutina"),
    path(
        "rutinas/toggle-activa/<int:rutina_id>/",
        views.toggle_rutina_activa,
        name="toggle_rutina_activa",
    ),
]
