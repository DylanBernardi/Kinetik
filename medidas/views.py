from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .models import MedidaCorporal

# Definición de campos (para iterar, validar y obtener etiquetas)
MEDIDA_FIELDS = [
    {"name": "pecho", "label": "Pecho", "min": 0, "max": 300},
    {"name": "brazo", "label": "Brazo izq.", "min": 0, "max": 80},
    {"name": "brazo_der", "label": "Brazo der.", "min": 0, "max": 80},
    # ... (Añadir el resto de campos con sus min/max si deseas validar rangos)
    {"name": "antebrazo", "label": "Antebrazo izq.", "min": 0, "max": 60},
    {"name": "antebrazo_der", "label": "Antebrazo der.", "min": 0, "max": 60},
    {"name": "cintura", "label": "Cintura", "min": 0, "max": 200},
    {"name": "gemelos", "label": "Gemelo der.", "min": 0, "max": 60},
    {"name": "gemelos_izq", "label": "Gemelo izq.", "min": 0, "max": 60},
    {"name": "cuello", "label": "Cuello", "min": 0, "max": 60},
    {"name": "pierna_izq", "label": "Pierna izq.", "min": 0, "max": 120},
    {"name": "pierna_der", "label": "Pierna der.", "min": 0, "max": 120},
]


# Función auxiliar para calcular el cambio
def calcular_cambio(anterior, actual):
    if anterior is not None and actual is not None:
        try:
            # Convertir a float para la resta, asegurando Decimal en el modelo
            diff = float(actual) - float(anterior)
            return f"{'+' if diff > 0 else ''}{diff:.1f} cm"
        except (ValueError, TypeError):
            return "-"
    return "-"


@login_required
def registro_medidas_ajax(request):
    if request.method == "GET":
        ultima_medicion = MedidaCorporal.objects.filter(usuario=request.user).first()

        if ultima_medicion:
            # CREAMOS UN DICCIONARIO PARA ALMACENAR LOS VALORES DE FORMA SEGURA
            # Esto convierte cada DecimalField a una cadena con formato internacional (punto)
            medidas_formato_html = {}

            for field in ultima_medicion._meta.fields:
                valor = getattr(ultima_medicion, field.name)
                if valor is not None and field.get_internal_type() == "DecimalField":
                    medidas_formato_html[field.name] = "{:.1f}".format(valor)

        else:
            medidas_formato_html = None

        context = {
            "ultima_medicion": medidas_formato_html,  # Usamos el diccionario ya formateado
        }
        return render(request, "registro_medidas.html", context)

    if request.method == "POST":
        medida_data = {"usuario": request.user}
        validation_errors = {}

        # 1. Extracción y Validación Manual
        for field in MEDIDA_FIELDS:
            field_name = field["name"]
            raw_value = request.POST.get(field_name)

            if raw_value and raw_value.strip():
                try:
                    decimal_value = Decimal(raw_value.replace(",", "."))

                    if decimal_value < field["min"] or decimal_value > field["max"]:
                        validation_errors[field_name] = (
                            f"{field['label']} debe estar entre {field['min']} y {field['max']}."
                        )
                        continue

                    medida_data[field_name] = decimal_value

                except InvalidOperation:
                    validation_errors[field_name] = (
                        f"El valor de {field['label']} no es un número válido."
                    )
            else:
                # Si está vacío o solo espacios, se registra como None (null=True en el modelo)
                medida_data[field_name] = None

        # 2. Manejo de Errores de Validación
        if validation_errors:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Error de validación. Revise los campos ingresados.",
                    "errors": validation_errors,
                },
                status=400,
            )  

        # 3. Guardar la Nueva Medida y Preparar Respuesta
        try:
            # Obtener el registro inmediatamente anterior ANTES de guardar el nuevo
            registro_anterior = MedidaCorporal.objects.filter(
                usuario=request.user
            ).first()

            # Crear y guardar el nuevo objeto
            nueva_medida = MedidaCorporal.objects.create(**medida_data)

            # 4. Generar datos de comparación para el frontend
            comparacion_data = []

            for field in MEDIDA_FIELDS:
                field_name = field["name"]

                valor_actual = getattr(nueva_medida, field_name)
                valor_anterior = (
                    getattr(registro_anterior, field_name)
                    if registro_anterior
                    else None
                )

                # Formatear valores para JSON/HTML
                valor_actual_str = (
                    f"{float(valor_actual):.1f}" if valor_actual is not None else "-"
                )
                valor_anterior_str = (
                    f"{float(valor_anterior):.1f}"
                    if valor_anterior is not None
                    else "-"
                )

                # Calcular la diferencia
                cambio = calcular_cambio(valor_anterior, valor_actual)

                comparacion_data.append(
                    {
                        "label": field["label"],
                        "anterior": valor_anterior_str,
                        "actual": valor_actual_str,
                        "cambio": cambio,
                    }
                )

            # 5. Devolver Respuesta JSON de Éxito
            return JsonResponse(
                {
                    "status": "success",
                    "message": "¡Registro guardado y tabla actualizada correctamente! ✅",
                    "data": comparacion_data,
                }
            )

        except Exception as e:
            # Manejar errores de base de datos
            print(f"Database error: {e}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Error interno del servidor al guardar los datos.",
                    "errors": {},
                },
                status=500,
            )
