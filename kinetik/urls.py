from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('',include('calculadoras.urls')),
    path('',include('medidas.urls')),
    path('',include('peso.urls')),
]
