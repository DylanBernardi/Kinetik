from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rutinas.models import Rutina, RutinaDia, DIAS_SEMANA, DetalleEjercicio, Ejercicios
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from collections import defaultdict

User = get_user_model()


@login_required(login_url="/login/")
def mis_rutinas(request):

    rutinas_del_usuario = Rutina.objects.filter(usuario=request.user).order_by("nombre")

    context = {
        "rutinas": rutinas_del_usuario,
        "titulo": f"Rutinas de {request.user.username}",
    }

    return render(request, "mis_rutinas.html", context)


def mostrar_rutina_semanal(request, rutina_id):
    return render(request, "mostrar_rutina_semanal.html")


def crear_rutina(request):
    # --- 1. Inicialización y Contexto Base ---
    nombre_rutina = ""
    errores = {}
    datos_precargados = {}  # Necesario si falla la validación del nombre
    opciones_ejercicio = Ejercicios.objects.all().order_by("nombre")

    if request.method == "POST":
        datos = request.POST

        # --- 2. Validar Rutina Base (CRÍTICO) ---
        nombre_rutina = datos.get("nombre", "").strip()
        if not nombre_rutina:
            errores["nombre"] = "El nombre de la rutina es obligatorio."

        # --- 3. Procesar y Guardar Datos ---
        if not errores:
            try:
                with transaction.atomic():

                    # A. Crear Rutina Base
                    nueva_rutina = Rutina.objects.create(
                        nombre=nombre_rutina, usuario=request.user
                    )

                    # B. Iterar y guardar los ejercicios por día
                    for num_dia, nombre_dia in DIAS_SEMANA:

                        # Obtener las listas de valores enviadas por el formulario (gracias a '[]')
                        ejercicios_ids = datos.getlist(f"dia_{num_dia}_ejercicio[]")
                        pesos = datos.getlist(f"dia_{num_dia}_peso[]")
                        repeticiones = datos.getlist(f"dia_{num_dia}_repeticiones[]")
                        series = datos.getlist(f"dia_{num_dia}_series[]")
                        descansos = datos.getlist(f"dia_{num_dia}_descanso[]")

                        datos_dia_guardado = zip(
                            ejercicios_ids, pesos, repeticiones, series, descansos
                        )
                        orden_dia = 1

                        for ej_id, peso, reps, sets, descanso in datos_dia_guardado:

                            # Intentamos convertir los tipos. Si falla, el bloque 'except' lo capturará.
                            try:
                                # Saltar filas vacías o si el ejercicio no está seleccionado
                                if not ej_id:
                                    continue

                                # Conversión y limpieza de tipos
                                ej_id = int(ej_id)
                                peso = float(peso) if peso else 0.0
                                reps = int(reps) if reps else 0
                                sets = int(sets) if sets else 0
                                descanso = int(descanso) if descanso else 0

                                # Verificación de existencia del ejercicio
                                if not Ejercicios.objects.filter(pk=ej_id).exists():
                                    messages.warning(
                                        request,
                                        f"Ejercicio inválido en el día {nombre_dia} y se ha ignorado.",
                                    )
                                    continue

                                # C. Crear DetalleEjercicio (El registro del ejercicio específico)
                                detalle = DetalleEjercicio.objects.create(
                                    ejercicio_id=ej_id,
                                    peso=peso,
                                    repeticiones=reps,
                                    series=sets,
                                    descanso=descanso,
                                )

                                # D. Crear RutinaDia (La relación día-rutina-ejercicio)
                                RutinaDia.objects.create(
                                    rutina=nueva_rutina,
                                    detalle_ejercicio=detalle,
                                    dia_semana=num_dia,  # Usamos el número del día (1 al 7)
                                    orden=orden_dia,
                                )
                                orden_dia += 1

                            except (ValueError, TypeError) as e:
                                # Capturamos errores de formato (ej. "a" en lugar de número)
                                messages.warning(
                                    request,
                                    f"Se ignoró un ejercicio en el día {nombre_dia} debido a un formato de datos incorrecto.",
                                )
                                continue  # Continuamos con el siguiente ejercicio

                messages.success(
                    request, f'Rutina "{nueva_rutina.nombre}" creada con éxito!'
                )
                return redirect("mis_rutinas")  # Redirigir a la lista de rutinas

            except Exception as e:
                messages.error(request, f"Error fatal al guardar la rutina. ({e})")

    # --- 4. Manejo de GET o POST inválido (Renderizar formulario) ---

    context = {
        "dias_semana": DIAS_SEMANA,
        "opciones_ejercicio": opciones_ejercicio,
        "errores": errores,
        "nombre_rutina_precargado": nombre_rutina,
        "datos_precargados": datos_precargados,  # Contendrá datos solo si falla validación de nombre
    }
    return render(request, "crear_rutina.html", context)


def eliminar_rutina(request, rutina_id):

    # 1. Busca la rutina por ID, devuelve 404 si no existe
    rutina = get_object_or_404(Rutina, pk=rutina_id)

    # 2. VERIFICACIÓN DE SEGURIDAD CRÍTICA
    # Solo el propietario (request.user) puede borrar la rutina
    if rutina.usuario == request.user:
        rutina_nombre = rutina.nombre
        rutina.delete()  # ¡Aquí se borra de la BD!

        # Opcional: Envía un mensaje de éxito al usuario
        messages.success(
            request, f'La rutina "{rutina_nombre}" ha sido eliminada correctamente.'
        )
    else:
        # Mensaje de error si el usuario no tiene permisos
        messages.error(request, "No tienes permiso para eliminar esta rutina.")

    # 3. Redirige a la lista de rutinas del usuario
    return redirect("mis_rutinas")


def editar_rutina(request, rutina_id):
    return render(request, "entrenamientos_casa.html")


def entrenamientos_casa(request):
    return render(request, "entrenamientos_casa.html")


def entrenamientos_gimnasio(request):
    return render(request, "entrenamientos_gimnasio.html")
