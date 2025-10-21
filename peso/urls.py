from django.contrib import admin
from django.urls import path
from peso import views

urlpatterns = [
path('registro_peso/',views.registro_peso, name="reg_peso"),]
