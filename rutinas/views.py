from django.shortcuts import render

# Create your views here.
def crear_rutinas(request):
    return render(request,'crear_rutinas.html')

def entrenamientos_casa(request):
    return render(request,'entrenamientos_casa.html')

def entrenamientos_gimnasio(request):
    return render(request,'entrenamientos_gimnasio.html')

def mis_rutinas(request):
    return render(request,'mis_rutinas.html')