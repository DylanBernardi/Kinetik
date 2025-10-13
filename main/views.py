from django.shortcuts import render

# Create your views here.
def inicio(request):
    return render(request,'index.html')

def login(request):
    return render(request,'login.html')

def registro(request):
    return render(request,'registro.html')