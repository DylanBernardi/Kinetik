// 1. VARIABLES GLOBALES
let filtroActual = 'todos';


// 2. FUNCIONES GLOBALES (Accedidas por el HTML)

function mostrarNotificacion(msg) {
    const notif = document.createElement('div');
    notif.className = 'notificacion-exito'; // Asegúrate de tener este CSS
    notif.textContent = msg;
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.style.opacity = 1; 
    }, 50);

    setTimeout(() => notif.remove(), 2500);
}

window.mostrarNotificacion = mostrarNotificacion;

/* Registra un nuevo peso ingresado por el usuario. */

function registrarPeso() {
    const pesoInput = document.getElementById('peso-actual');
    const peso = parseFloat(pesoInput.value);
    
    if (!peso || peso <= 0) {
        
        mostrarNotificacion('Por favor ingresa un peso válido', 'error'); 
        return;
    }
    
    // Obtener registros existentes
    const registrosPeso = JSON.parse(localStorage.getItem('registrosPeso')) || [];
    
    // Crear nuevo registro
    const nuevoRegistro = {
        id: Date.now(),
        fecha: new Date().toISOString(), // Formato ISO para fácil ordenamiento
        peso: peso,
        fechaFormateada: new Date().toLocaleDateString('es-ES')
    };
    
    // Agregar al array y guardar
    registrosPeso.push(nuevoRegistro);
    localStorage.setItem('registrosPeso', JSON.stringify(registrosPeso));
    
    // Actualizar interfaz
    actualizarTablaPeso();
    actualizarEstadisticas();
    
    // Limpiar input
    pesoInput.value = '';
    
    // Mostrar mensaje de éxito
    mostrarNotificacion('Peso registrado exitosamente');
}

window.registrarPeso = registrarPeso;

/**
 * Cambia el filtro de registros y actualiza la tabla./
 * @param {string} filtro - El tipo de filtro a aplicar ('todos', 'ultimo-mes', 'ultimos-3-meses').
 */

function filtrarRegistros(filtro, event) {
    filtroActual = filtro;
    
    // Actualizar botones activos
    document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));

    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Actualizar tabla
    actualizarTablaPeso();
}
window.filtrarRegistros = filtrarRegistros;

/**
 * Elimina un registro por su ID.
 * @param {number} id - */
function eliminarRegistro(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este registro?')) {
        let registrosPeso = JSON.parse(localStorage.getItem('registrosPeso')) || [];
        // Filtramos para crear un nuevo array sin el registro con el ID dado
        registrosPeso = registrosPeso.filter(r => r.id !== id);
        localStorage.setItem('registrosPeso', JSON.stringify(registrosPeso));
        
        actualizarTablaPeso();
        actualizarEstadisticas();
        mostrarNotificacion('Registro eliminado');
    }
}
window.eliminarRegistro = eliminarRegistro;

// 3. FUNCIONES INTERNAS (Auxiliares)

/**
 * Filtra los registros según el período de tiempo seleccionado.
 * @param {Array} registros 
 * @returns {Array} - */

function filtrarPorFecha(registros) {
    const ahora = new Date();
    
    switch(filtroActual) {
        case 'ultimo-mes':
            // Calcula la fecha de hace un mes
            const unMesAtras = new Date(ahora.getFullYear(), ahora.getMonth() - 1, ahora.getDate());
            return registros.filter(r => new Date(r.fecha) >= unMesAtras);
        
        case 'ultimos-3-meses':
            // Calcula la fecha de hace tres meses
            const tresMesesAtras = new Date(ahora.getFullYear(), ahora.getMonth() - 3, ahora.getDate());
            return registros.filter(r => new Date(r.fecha) >= tresMesesAtras);
        
        default:
            // 'todos' o cualquier otro valor
            return registros;
    }
}

/* Actualiza la tabla de historial de peso en la interfaz.*/
function actualizarTablaPeso() {
    const registrosPeso = JSON.parse(localStorage.getItem('registrosPeso')) || [];
    const tbody = document.getElementById('peso-comparison-body');
    
    if (!tbody) return; // Salir si el elemento no existe
    
    tbody.innerHTML = '';
    
    // 1. Filtrar registros
    let registrosFiltrados = filtrarPorFecha(registrosPeso);
    
    // 2. Ordenar por fecha (más recientes primero) para la visualización de la tabla
    registrosFiltrados.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
    
    if (registrosFiltrados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No hay registros de peso</td></tr>';
        return;
    }

    // 3. Iterar y renderizar
    registrosFiltrados.forEach((registro, index) => {
        // Necesitamos encontrar el registro cronológicamente anterior a este registro *filtrado*.
        // Para calcular el cambio, debemos usar el registro siguiente en el array *ordenado inversamente*.
        const registroAnteriorOrdenado = registrosFiltrados[index + 1];
        
        const pesoAnterior = registroAnteriorOrdenado ? registroAnteriorOrdenado.peso : null;
        const cambio = pesoAnterior !== null ? registro.peso - pesoAnterior : 0;
        
        const cambioClase = cambio > 0 ? 'positive' : cambio < 0 ? 'negative' : 'neutral';
        const cambioTexto = cambio === 0 ? '0.0' : (cambio > 0 ? `+${cambio.toFixed(1)}` : cambio.toFixed(1));
        
        const pesoAnteriorTexto = pesoAnterior ? pesoAnterior.toFixed(1) + ' kg' : '--'; // Para visualización

        const fila = `
            <tr>
                <td>${registro.fechaFormateada}</td>
                <td>${registro.peso.toFixed(1)} kg</td>
                <td class="peso-change ${cambioClase}">${cambioTexto} kg</td>
                <td>
                    <button class="btn-eliminar" onclick="eliminarRegistro(${registro.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        
        tbody.insertAdjacentHTML('beforeend', fila);
    });
}


/* Calcula y actualiza las estadísticas clave (último peso, cambio reciente, total). */
function actualizarEstadisticas() {
    const registrosPeso = JSON.parse(localStorage.getItem('registrosPeso')) || [];
    
    const ultimoPesoElement = document.getElementById('ultimo-peso');
    const cambioRecienteElement = document.getElementById('cambio-reciente');
    const totalRegistrosElement = document.getElementById('total-registros');
    
    // Manejo de elementos nulos por si no existen en el HTML de la página actual
    if (!ultimoPesoElement || !cambioRecienteElement || !totalRegistrosElement) return;

    if (registrosPeso.length === 0) {
        ultimoPesoElement.textContent = '-- kg';
        cambioRecienteElement.textContent = '-- kg';
        totalRegistrosElement.textContent = '0';
        cambioRecienteElement.className = '';
        return;
    }
    
    // Ordenar por fecha (más recientes primero)
    const registrosOrdenados = registrosPeso.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
    
    // Último peso
    const ultimoPeso = registrosOrdenados[0].peso;
    ultimoPesoElement.textContent = `${ultimoPeso.toFixed(1)} kg`;
    
    // Cambio reciente (entre el último y el penúltimo)
    if (registrosOrdenados.length > 1) {
        const cambio = ultimoPeso - registrosOrdenados[1].peso;
        const cambioTexto = cambio > 0 ? `+${cambio.toFixed(1)}` : cambio.toFixed(1);
        
        cambioRecienteElement.textContent = `${cambioTexto} kg`;
        // Aplicar clases CSS para color
        cambioRecienteElement.className = cambio > 0 ? 'positive' : cambio < 0 ? 'negative' : 'neutral';
    } else {
        cambioRecienteElement.textContent = '-- kg';
        cambioRecienteElement.className = '';
    }
    
    // Total registros
    totalRegistrosElement.textContent = registrosPeso.length;
}

document.addEventListener('DOMContentLoaded', function() {
    // ----------------------------------------------------
    // LÓGICA DE PRUEBA: 
    // Si no hay datos, carga los datos de prueba.
    // Una vez que uses el botón "Registrar Peso" real,
    // este código dejará de ejecutarse hasta que borres el localStorage.
    // ----------------------------------------------------
    const registrosExistentes = localStorage.getItem('registrosPeso');
    if (!registrosExistentes || JSON.parse(registrosExistentes).length === 0) {
        console.log("Cargando datos de prueba...");
        crearDatosDePrueba();
    }
    // ----------------------------------------------------
    
    // Inicializar la tabla y las estadísticas al cargar la página
    actualizarTablaPeso();
    actualizarEstadisticas();
    
    // Asegurar que el botón "Todos" esté activo al inicio (si existe)
    const btnTodos = document.querySelector('.btn-filtro[onclick*="todos"]');
    if (btnTodos) {
        btnTodos.classList.add('active');
    }
});


function crearDatosDePrueba() {
    const ahora = new Date();
    
    // Función auxiliar para obtener fechas y formatearlas
    const obtenerRegistroDePrueba = (mesesAtras, peso) => {
        const fecha = new Date(ahora.getFullYear(), ahora.getMonth() - mesesAtras, ahora.getDate());
        return {
            // Usamos un ID basado en la fecha + un número random para asegurar que sea único
            id: fecha.getTime() + Math.floor(Math.random() * 1000), 
            fecha: fecha.toISOString(),
            peso: peso,
            fechaFormateada: fecha.toLocaleDateString('es-ES')
        };
    };

    const registrosDePrueba = [
        // 1. Registro MUY antiguo (para asegurar que queda fuera de 3 meses)
        obtenerRegistroDePrueba(5, 75.0),
        
        // 2. Registro que queda FUERA del último mes, pero DENTRO de 3 meses (ej: hace 2 meses)
        obtenerRegistroDePrueba(2, 78.5),
        
        // 3. Registro que queda DENTRO del último mes (ej: hace 15 días)
        obtenerRegistroDePrueba(0, 80.2), 
        
        // 4. Registro de HOY (el más reciente)
        obtenerRegistroDePrueba(0, 81.0), 
        
        // 5. Registro al límite de 3 meses (ej: hace 89 días)
        obtenerRegistroDePrueba(2.9, 77.0), 
    ];

    // NOTA: Sobreescribimos cualquier dato existente para que la prueba sea consistente.
    localStorage.setItem('registrosPeso', JSON.stringify(registrosDePrueba));
}