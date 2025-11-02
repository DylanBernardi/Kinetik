// Variables globales
let filtroActual = "todos";

// 2. FUNCIONES GLOBALES (Accedidas por el HTML)

function mostrarNotificacion(msg, tipo = 'exito') {
    const notif = document.createElement("div");
    notif.className = `notificacion-${tipo}`; // exito o error
    notif.textContent = msg;
    document.body.appendChild(notif);

    setTimeout(() => {
        notif.style.opacity = 1;
    }, 50);

    setTimeout(() => notif.remove(), 2500);
}

window.mostrarNotificacion = mostrarNotificacion;

/* Registra un nuevo peso ingresado por el usuario. */
async function registrarPeso(event) {
    // Prevenir el comportamiento por defecto del formulario
    if (event) {
        event.preventDefault();
    }
    
    const pesoInput = document.getElementById("peso-actual");
    // Si el campo está vacío, mostrar mensaje
    if (!pesoInput.value.trim()) {
        mostrarNotificacion("Por favor ingresa un peso", "error");
        return;
    }

    const peso = parseFloat(pesoInput.value);
    if (peso <= 0) {
        mostrarNotificacion("El peso debe ser mayor a 0", "error");
        return;
    }

    try {
        // Obtener el token CSRF del formulario
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/registro_peso/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ peso: peso })
        });

        // Verificar si la respuesta es JSON antes de intentar parsearla
        const contentType = response.headers.get("content-type");
        let data;
        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Error al guardar el peso');
            }
            // Limpiar el input después de un registro exitoso
            pesoInput.value = "";
            // Actualizar la tabla
            await actualizarTablaPeso();
            mostrarNotificacion("Peso registrado exitosamente");
        } else {
            throw new Error('Error en el servidor');
        }
    } catch (error) {
        mostrarNotificacion(error.message, "error");
        console.error('Error:', error);
    }
}

window.registrarPeso = registrarPeso;

/**
 * Cambia el filtro de registros y actualiza la tabla.
 * @param {string} filtro - El tipo de filtro a aplicar ('todos', 'ultimo_mes', '3_meses').
 */
async function filtrarRegistros(filtro, event) {
    filtroActual = filtro;

    // Actualizar botones activos
    document
        .querySelectorAll(".btn-filtro")
        .forEach((btn) => btn.classList.remove("active"));

    if (event && event.target) {
        event.target.classList.add("active");
    }

    // Actualizar tabla
    await actualizarTablaPeso();
}

window.filtrarRegistros = filtrarRegistros;

/**
 * Elimina un registro por su ID.
 * @param {number} id - ID del registro a eliminar
 */
async function eliminarRegistro(id) {
    if (!confirm("¿Estás seguro de que quieres eliminar este registro?")) {
        return;
    }

    try {
        const response = await fetch(`/registro_peso/eliminar/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar el registro');
        }

        await actualizarTablaPeso();
        mostrarNotificacion("Registro eliminado exitosamente");
    } catch (error) {
        mostrarNotificacion(error.message, "error");
    }
}

window.eliminarRegistro = eliminarRegistro;

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 3. FUNCIONES INTERNAS (Auxiliares)

/**
 * Actualiza la tabla de historial de peso en la interfaz.
 * Obtiene los datos del backend y actualiza la UI.
 */
// Función para actualizar solo la tabla sin tocar el formulario
async function actualizarTablaPeso() {
    const tbody = document.getElementById("peso-comparison-body");
    if (!tbody) return;

    try {
        const response = await fetch(`/registro_peso/obtener/?filtro=${filtroActual}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error('Error al obtener los registros');
        }

        let data;
        const text = await response.text();
        try {
            data = JSON.parse(text);
        } catch (error) {
            console.error('Error parsing JSON:', error);
            console.error('Response text:', text);
            throw new Error('La respuesta del servidor no es JSON válido');
        }

        // Actualizar estadísticas
        actualizarEstadisticas(data.estadisticas);
        
        // Limpiar y actualizar la tabla
        tbody.innerHTML = "";

        if (data.registros.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No hay registros de peso</td></tr>';
            return;
        }

        // Renderizar registros
        data.registros.forEach(registro => {
            const cambioClase = registro.cambio > 0 ? "positive" : 
                               registro.cambio < 0 ? "negative" : "neutral";
            const cambioTexto = registro.cambio === 0 ? "0.0" : 
                               registro.cambio > 0 ? `+${registro.cambio.toFixed(1)}` : 
                               registro.cambio.toFixed(1);

            const fila = `
                <tr>
                    <td>${registro.fecha}</td>
                    <td>${registro.peso.toFixed(1)} kg</td>
                    <td class="peso-change ${cambioClase}">${cambioTexto} kg</td>
                    <td>
                        <button class="btn-eliminar" type="button" onclick="eliminarRegistro(${registro.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;

            tbody.insertAdjacentHTML("beforeend", fila);
        });


    } catch (error) {
        mostrarNotificacion(error.message, "error");
        tbody.innerHTML = '<tr><td colspan="4">Error al cargar los registros</td></tr>';
    }
}

/**
 * Actualiza las estadísticas en la interfaz.
 * @param {Object} estadisticas - Objeto con las estadísticas del backend
 */
function actualizarEstadisticas(estadisticas) {
    const ultimoPesoElement = document.getElementById("ultimo-peso");
    const cambioRecienteElement = document.getElementById("cambio-reciente");
    const totalRegistrosElement = document.getElementById("total-registros");

    if (!ultimoPesoElement || !cambioRecienteElement || !totalRegistrosElement) return;

    if (estadisticas.total_registros === 0) {
        ultimoPesoElement.textContent = "-- kg";
        cambioRecienteElement.textContent = "-- kg";
        totalRegistrosElement.textContent = "0";
        cambioRecienteElement.className = "";
        return;
    }

    // Actualizar valores
    ultimoPesoElement.textContent = `${estadisticas.ultimo_peso.toFixed(1)} kg`;
    totalRegistrosElement.textContent = estadisticas.total_registros;

    // Actualizar cambio reciente
    const cambioTexto = estadisticas.cambio_reciente === 0 ? "0.0" :
                        estadisticas.cambio_reciente > 0 ? `+${estadisticas.cambio_reciente.toFixed(1)}` :
                        estadisticas.cambio_reciente.toFixed(1);
    
    cambioRecienteElement.textContent = `${cambioTexto} kg`;
    cambioRecienteElement.className = estadisticas.cambio_reciente > 0 ? "positive" :
                                      estadisticas.cambio_reciente < 0 ? "negative" :
                                      "neutral";
}

document.addEventListener("DOMContentLoaded", async function () {
    // Inicializar la tabla al cargar la página
    await actualizarTablaPeso();

    // Asegurar que el botón "Todos" esté activo al inicio
    const btnTodos = document.querySelector('.btn-filtro[onclick*="todos"]');
    if (btnTodos) {
        btnTodos.classList.add("active");
    }
});