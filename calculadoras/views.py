from django.shortcuts import render
import json
from django.http import JsonResponse
import math


def calculadora_mr(request):
    return render(request, "calculadora_mr.html")


def calculadora_rm(request):
    return render(request, "calculadora_rm.html")


def calculadora_mr_api(request):
    try:
        # Cargamos el Json
        data = json.loads(request.body)

        # Guardamos los datos
        peso = float(data.get("peso", 0))
        edad = int(data.get("edad", 0))
        sexo = data.get("sexo", "femenino")
        actividad = data.get("actividad", "sedentario")
        objetivo = data.get("objetivo", "mantener")

        altura_masculino = 170
        altura_femenino = 160

        if sexo == "masculino":
            mr = 88.36 + (13.4 * peso) + (5 * altura_masculino) - (6.8 * edad)
        else:
            mr = 447.6 + (9.2 * peso) + (3.1 * altura_femenino) - (4.3 * edad)

        factor = 1.2
        if actividad == "ligero":
            factor = 1.375
        elif actividad == "moderado":
            factor = 1.55
        elif actividad == "intenso":
            factor = 1.725
        elif actividad == "muy_intenso":
            factor = 1.9

        calorias_mantenimiento = mr * factor
        calorias = calorias_mantenimiento

        if objetivo == "bajar":
            calorias -= 500
        elif objetivo == "subir":
            calorias += 500

        proteinas_gr = round(peso * 2)
        proteinas_kcal = proteinas_gr * 4

        grasas_kcal = calorias * 0.25
        grasas_gr = round(grasas_kcal / 9)

        carbohidratos_kcal = calorias - (proteinas_kcal + grasas_kcal)
        carbohidratos_gr = round(carbohidratos_kcal / 4)  # 4 kcal/g

        # Creamos la respuesta
        response_data = {
            "calorias_totales": round(calorias),
            "objetivo": objetivo,
            "proteinas_gr": proteinas_gr,
            "grasas_gr": grasas_gr,
            "carbohidratos_gr": carbohidratos_gr,
            "proteinas_porcentaje": (
                round((proteinas_kcal / calorias) * 100) if calorias > 0 else 0
            ),
            "grasas_porcentaje": 25,
            "carbohidratos_porcentaje": (
                round((carbohidratos_kcal / calorias) * 100) if calorias > 0 else 0
            ),
        }

        return JsonResponse(response_data)

    except (ValueError, KeyError, TypeError, ZeroDivisionError) as e:
        return JsonResponse(
            {"error": f"Invalid input or calculation error: {str(e)}"}, status=400
        )


def calculadora_rm_api(request):
    try:
        # Cargamos el Json
        data = json.loads(request.body)

        # Guardamos datos
        peso = float(data.get("peso", 0))
        reps = int(data.get("reps", 0))

        # Validacion
        if peso <= 0 or reps <= 0 or reps > 15:
            return JsonResponse(
                {
                    "error": "Peso y repeticiones deben ser valores positivos y reps <= 15."
                },
                status=400,
            )

        # Calculamos RM
        rm = peso / (1.0278 - 0.0278 * reps)

        # Generamos la tabla
        table_data = []
        for i in range(1, 16):

            porcentaje_decimal = 1.0278 - 0.0278 * i
            porcentaje = porcentaje_decimal * 100

            # Calculamos peso recomendado
            peso_recomendado = rm * porcentaje_decimal

            peso_ajustado = math.ceil(peso_recomendado * 2) / 2

            table_data.append(
                {"reps": i, "peso": peso_ajustado, "porcentaje": round(porcentaje)}
            )

        # Preparamos la respuesta
        response_data = {"rm": round(rm), "input_reps": reps, "table_rows": table_data}

        return JsonResponse(response_data)

    except (ValueError, KeyError, TypeError) as e:
        return JsonResponse(
            {"error": f"Error de entrada de datos: {str(e)}"}, status=400
        )

    except ZeroDivisionError:
        return JsonResponse(
            {
                "error": "División por cero. Asegúrate de que las repeticiones sean válidas."
            },
            status=400,
        )
