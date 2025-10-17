from django.contrib import admin
from django.urls import path
from calculadoras import views

urlpatterns = [
path('calculadora_rm/',views.calculadora_rm, name="calc_rm"),
path('calculadora_mr/',views.calculadora_mr, name="calc_mr"),
]
