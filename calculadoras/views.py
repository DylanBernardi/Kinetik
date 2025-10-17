from django.shortcuts import render

# Create your views here.
def calculadora_mr(request):
    return render(request,'calculadora_mr.html')

def calculadora_rm(request):
    return render(request,'calculadora_rm.html')

