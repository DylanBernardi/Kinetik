from django.contrib import admin
from django.urls import path
from calculadoras import views

urlpatterns = [
    path("calculadora_rm/", views.calculadora_rm, name="calc_rm"),
    path("calculadora_mr/", views.calculadora_mr, name="calc_mr"),
    path("calculadora_mr/api", views.calculadora_mr_api, name="calc_mr_api"),
    path("calculadora_rm/api", views.calculadora_rm_api, name="calc_rm_api"),
]
