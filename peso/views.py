from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from .models import RegistroPeso
import json
import random

@login_required
def registro_peso(request):
    return render(request, "registro_peso.html")

@login_required
@require_http_methods(["POST"])
def guardar_peso(request):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Datos inválidos. Se requiere JSON válido.'
            }, status=400)

        if 'peso' not in data:
            return JsonResponse({
                'error': 'Falta el campo peso en la solicitud'
            }, status=400)
        
        try:
            peso = Decimal(str(data['peso']))
        except (ValueError, InvalidOperation, TypeError):
            return JsonResponse({
                'error': 'El peso debe ser un número válido'
            }, status=400)
        
        if peso <= 0 or peso > 999.99:
            return JsonResponse({
                'error': 'El peso debe ser un valor positivo y menor a 1000 kg'
            }, status=400)

        registro = RegistroPeso.objects.create(
            usuario=request.user,
            peso=peso
        )

        return JsonResponse({
            'mensaje': 'Peso registrado exitosamente',
            'peso': float(registro.peso),
            'fecha': registro.fecha_registro.strftime('%d/%m/%Y'),
            'id': registro.id
        })
    except (ValueError, InvalidOperation):
        return JsonResponse({
            'error': 'El peso debe ser un número válido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error al guardar el peso'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def obtener_registros(request):
    try:
        # Configurar el content type de la respuesta
        response = JsonResponse({})
        response['Content-Type'] = 'application/json'
        
        filtro = request.GET.get('filtro', 'todos')
        hoy = timezone.now()
        
        # Base query
        registros = RegistroPeso.objects.filter(usuario=request.user)
        
        # Aplicar filtro temporal
        if filtro == 'ultimo_mes':
            fecha_inicio = hoy - timedelta(days=30)
            registros = registros.filter(fecha_registro__gte=fecha_inicio)
        elif filtro == '3_meses':
            fecha_inicio = hoy - timedelta(days=90)
            registros = registros.filter(fecha_registro__gte=fecha_inicio)
        
        # Ordenar por fecha descendente
        registros = registros.order_by('-fecha_registro')
    
        # Preparar datos para la respuesta
        datos = []
        for registro in registros:
            # Calcular el cambio respecto al registro anterior
            cambio = 0
            try:
                registro_anterior = registros.filter(
                    fecha_registro__lt=registro.fecha_registro
                ).first()
                if registro_anterior:
                    cambio = float(registro.peso - registro_anterior.peso)
            except:
                pass

            datos.append({
                'id': registro.id,
                'fecha': registro.fecha_registro.strftime('%d/%m/%Y'),
                'peso': float(registro.peso),
                'cambio': round(cambio, 1)
            })
        
        # Obtener estadísticas
        if datos:
            ultimo_peso = datos[0]['peso']
            cambio_reciente = datos[0]['cambio']
            total_registros = len(datos)
        else:
            ultimo_peso = 0
            cambio_reciente = 0
            total_registros = 0

        response_data = {
            'registros': datos,
            'estadisticas': {
                'ultimo_peso': ultimo_peso,
                'cambio_reciente': cambio_reciente,
                'total_registros': total_registros
            }
        }
        
        return JsonResponse(response_data, safe=False, content_type='application/json')
    except Exception as e:
        return JsonResponse({
            'error': 'Error al obtener los registros'
        }, status=500)

@login_required
@require_http_methods(["DELETE"])
def eliminar_registro(request, registro_id):
    try:
        registro = RegistroPeso.objects.get(id=registro_id, usuario=request.user)
        registro.delete()
        return JsonResponse({
            'mensaje': 'Registro eliminado exitosamente'
        })
    except RegistroPeso.DoesNotExist:
        return JsonResponse({
            'error': 'Registro no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': 'Error al eliminar el registro'
        }, status=500)

@login_required
def generar_datos_prueba(request):
    try:
        # Eliminar registros existentes del usuario
        RegistroPeso.objects.filter(usuario=request.user).delete()
        
        # Generar registros de los últimos 4 meses
        ahora = timezone.now()
        
        for dias_atras in range(120, 0, -5):  # Del más antiguo al más reciente
            # Calcular fecha específica para cada registro
            fecha_registro = ahora - timedelta(days=dias_atras)
            fecha_registro = fecha_registro.replace(hour=8, minute=0, second=0, microsecond=0)
            
            # Generar peso base entre 70 y 80 kg
            if dias_atras == 120:  # Primer registro
                peso_base = Decimal('75.0')
            else:
                # Variar el peso anterior entre -0.3 y +0.3 kg
                peso_base += Decimal(str(random.uniform(-0.3, 0.3)))
            
            # Crear el registro con la fecha específica
            registro = RegistroPeso(
                usuario=request.user,
                peso=peso_base,
                fecha_registro=fecha_registro
            )
            # Guardar directamente en la base de datos para mantener la fecha
            registro.save()
            
            # Actualizar el peso base con una tendencia
            peso_base += Decimal(str(random.uniform(-0.2, 0.3)))
        
        return JsonResponse({
            'mensaje': 'Datos de prueba generados exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'error': 'Error al generar datos de prueba'
        }, status=500)
