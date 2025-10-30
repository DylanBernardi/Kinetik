from django.contrib import admin
from django.urls import path
from medidas import views

urlpatterns = [
    path("registro_medidas/", views.registro_medidas_ajax, name="reg_med"),
]
