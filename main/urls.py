from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
path('',views.inicio, name="inicio"),
path('login/',views.login, name="login"),
path('registro/',views.registro, name="registro"),

]
