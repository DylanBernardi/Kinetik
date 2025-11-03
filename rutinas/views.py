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


def mostrar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)

    detalles_rutina = (
        RutinaDia.objects.filter(rutina=rutina)
        .select_related(
            "detalle_ejercicio__ejercicio" 
        )
        .order_by("dia_semana", "orden")
    )

    rutina_agrupada = defaultdict(list)

    for rutina_dia in detalles_rutina:
        dia_semana_num = rutina_dia.dia_semana
        detalle = rutina_dia.detalle_ejercicio
        ejercicio = detalle.ejercicio

        rutina_agrupada[dia_semana_num].append(
            {
                "nombre_ejercicio": ejercicio.nombre,
                "peso": detalle.peso,
                "repeticiones": detalle.repeticiones,
                "series": detalle.series,
                "descanso": detalle.descanso,
                "orden": rutina_dia.orden,
            }
        )

    # 3. Preparar el contexto para la plantilla
    contexto = {
        "rutina": rutina,
        "rutina_agrupada": dict(rutina_agrupada),  # Convertir a dict para el template
        "dias_semana": DIAS_SEMANA,  # Necesario para los encabezados de la tabla (1=Lunes, 2=Martes, etc.)
    }

    return render(request, "mostrar_rutina.html", contexto)


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

    rutina = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)

    # Obtener todos los ejercicios disponibles para el dropdown
    ejercicios_disponibles = Ejercicios.objects.all().order_by("nombre")
    
    # Días de la semana, necesarios para iterar la estructura del formulario
    dias_semana_list = DIAS_SEMANA

    # 2. Manejo de Petición POST (Guardar cambios)
    if request.method == "POST":
        nombre_rutina = request.POST.get("nombre_rutina")

        if not nombre_rutina:
            messages.error(request, "El nombre de la rutina es obligatorio.")
            return redirect("editar_rutina", rutina_id=rutina.id)

        # Actualizar el nombre
        rutina.nombre = nombre_rutina
        rutina.save()

        # Eliminar registros antiguos antes de guardar los nuevos
        RutinaDia.objects.filter(rutina=rutina).delete()

        # Iterar sobre los días de la semana y guardar los ejercicios
        for num_dia, _ in dias_semana_list:
            # Obtener todas las listas de ejercicios para este día (puede haber varias)
            ejercicios_del_dia = request.POST.getlist(f"dia_{num_dia}_ejercicio[]")
            series_del_dia = request.POST.getlist(f"dia_{num_dia}_series[]")
            repeticiones_del_dia = request.POST.getlist(f"dia_{num_dia}_repeticiones[]")
            pesos_del_dia = request.POST.getlist(f"dia_{num_dia}_peso[]")
            descansos_del_dia = request.POST.getlist(f"dia_{num_dia}_descanso[]")

            # Recorrer las listas paralelas para crear/guardar cada DetalleEjercicio
            for i, ejercicio_id in enumerate(ejercicios_del_dia):
                if not ejercicio_id:
                    continue  # Saltar si el ejercicio no fue seleccionado

                try:
                    detalle = DetalleEjercicio.objects.create(
                        ejercicio_id=ejercicio_id,
                        series=series_del_dia[i] if series_del_dia[i] else 0,
                        repeticiones=(
                            repeticiones_del_dia[i] if repeticiones_del_dia[i] else 0
                        ),
                        peso=pesos_del_dia[i] if pesos_del_dia[i] else 0,
                        descanso=descansos_del_dia[i] if descansos_del_dia[i] else 0,
                    )

                    # Crear el enlace RutinaDia
                    RutinaDia.objects.create(
                        rutina=rutina,
                        dia_semana=num_dia,
                        orden=i + 1,  # El orden en el formulario es i+1
                        detalle_ejercicio=detalle,
                    )
                except IndexError:
                    # Manejar el caso donde las listas no tienen la misma longitud
                    messages.error(
                        request,
                        f"Error de datos al guardar la rutina en el día {num_dia}.",
                    )
                    break
                except Exception as e:
                    messages.error(request, f"Error al guardar los detalles: {e}")

        return redirect(
            "mostrar_rutina", rutina_id=rutina.id
        )  


    detalles_rutina = (
        RutinaDia.objects.filter(rutina=rutina)
        .select_related("detalle_ejercicio__ejercicio")
        .order_by("dia_semana", "orden")
    )

    # Estructura para agrupar los datos actuales: {dia: [detalle1, detalle2, ...]}
    rutina_actual = defaultdict(list)
    for rd in detalles_rutina:
        rutina_actual[rd.dia_semana].append(
            {
                "rutina_dia_id": rd.id,
                "ejercicio_id": rd.detalle_ejercicio.ejercicio_id,
                "nombre_ejercicio": rd.detalle_ejercicio.ejercicio.nombre,
                "series": rd.detalle_ejercicio.series,
                "repeticiones": rd.detalle_ejercicio.repeticiones,
                "peso": rd.detalle_ejercicio.peso,
                "descanso": rd.detalle_ejercicio.descanso,
                "orden": rd.orden,
            }
        )

    contexto = {
        "rutina": rutina,
        "rutina_actual": dict(rutina_actual),
        "ejercicios_disponibles": ejercicios_disponibles,
        "dias_semana": dias_semana_list,
    }
    return render(request, "editar_rutina.html", contexto)


def toggle_rutina_activa(request, rutina_id):

    rutina_seleccionada = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)

    nuevo_estado = not rutina_seleccionada.activo

    if nuevo_estado:

        Rutina.objects.filter(usuario=request.user, activo=True).update(activo=False)

        rutina_seleccionada.activo = True
        rutina_seleccionada.save()

    else:
        rutina_seleccionada.activo = False
        rutina_seleccionada.save()

        messages.info(request, f"Rutina '{rutina_seleccionada.nombre}' desactivada.")
    return redirect("mis_rutinas")

def entrenamientos_casa(request):
    return render(request, "entrenamientos_casa.html")

def entrenamientos_gimnasio(request):
    return render(request, "entrenamientos_gimnasio.html")
