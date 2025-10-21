from django.contrib import admin
from django.urls import path
from rutinas import views

urlpatterns = [
path('crear_rutinas/',views.crear_rutinas, name="crear_rutinas"),
path('entrenamientos_casa/',views.entrenamientos_casa, name="entrenamientos_casa"),
path('entrenamientos_gimnasio/',views.entrenamientos_gimnasio, name="entrenamientos_gimnasio"),
path('mis_rutinas/',views.mis_rutinas, name="mis_rutinas"),
]
