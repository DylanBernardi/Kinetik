document.addEventListener('DOMContentLoaded', function() {

    // 1. Configuración y Event Listener Principal
    const medidasForm = document.getElementById('medidasForm');

if (medidasForm) {
    medidasForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Definición de campos 
        const campos = [
            { id: 'pecho', label: 'Pecho' },
            { id: 'brazo', label: 'Brazo izq.' },
            { id: 'brazo_der', label: 'Brazo der.' },
            { id: 'antebrazo', label: 'Antebrazo izq.' },
            { id: 'antebrazo_der', label: 'Antebrazo der.' },
            { id: 'cintura', label: 'Cintura' },
            { id: 'pierna_izq', label: 'Pierna izq.' },
            { id: 'pierna_der', label: 'Pierna der.' },
            { id: 'gemelos', label: 'Gemelo der.' },
            { id: 'gemelos_izq', label: 'Gemelo izq.' },
            { id: 'cuello', label: 'Cuello' }
        ];

        // Guardar registro actual
        const registroActual = {};
        campos.forEach(campo => {
            const elemento = document.getElementById(campo.id);
            if (elemento) {
                registroActual[campo.id] = elemento.value;
            }
        });

        // Obtener último registro
        const ultimoRegistro = JSON.parse(localStorage.getItem('ultimoRegistroMedidas'));

        // Guardar nuevo registro
        localStorage.setItem('ultimoRegistroMedidas', JSON.stringify(registroActual));

        // Llamada a las funciones de visualización
        mostrarNotificacion('¡Registro guardado correctamente!');
        mostrarComparacion(ultimoRegistro, registroActual, campos);


        //LIMPIEZA DE TODOS LOS CAMPOS

        campos.forEach(campo => {
            const elemento = document.getElementById(campo.id);
            if (elemento) {
                elemento.value = ''; 
            }
        });
        
    });
}

    // Cargar último registro guardado y mostrar la tabla de comparación si existe
    const ultimoRegistroGuardado = JSON.parse(localStorage.getItem('ultimoRegistroMedidas'));
    if (ultimoRegistroGuardado) {
        const campos = [
            { id: 'pecho', label: 'Pecho' },
            { id: 'brazo', label: 'Brazo izq.' },
            { id: 'brazo_der', label: 'Brazo der.' },
            { id: 'antebrazo', label: 'Antebrazo izq.' },
            { id: 'antebrazo_der', label: 'Antebrazo der.' },
            { id: 'cintura', label: 'Cintura' },
            { id: 'pierna_izq', label: 'Pierna izq.' },
            { id: 'pierna_der', label: 'Pierna der.' },
            { id: 'gemelos', label: 'Gemelo der.' },
            { id: 'gemelos_izq', label: 'Gemelo izq.' },
            { id: 'cuello', label: 'Cuello' }
        ];
    }
});


// 2. Funciones Auxiliares (Deben ser accesibles globalmente o dentro de DOMContentLoaded)

// FUNCIÓN DE COMPARACIÓN
function mostrarComparacion(ultimo, actual, campos) {
    const comparacionContenido = document.getElementById('comparacionContenido');
    if (!comparacionContenido) return;
    
    let html = '';
    if (!ultimo) {
        html = '<p>Este es tu primer registro.</p>';
    } else {
        html = '<table style="width:100%;text-align:center;"><tr><th>Medida</th><th>Anterior</th><th>Actual</th><th>Cambio</th></tr>';
        campos.forEach(campo => {
            const prev = ultimo[campo.id] || '-';
            const curr = actual[campo.id] || '-';
            let cambio = '-';
            
            if (prev !== '-' && curr !== '-') {
                const diff = (parseFloat(curr) - parseFloat(prev)).toFixed(1);
                cambio = (diff > 0 ? '+' : '') + diff + ' cm';
            }
            
            html += `<tr>
                <td>${campo.label}</td>
                <td>${prev} cm</td>
                <td>${curr} cm</td>
                <td>${cambio}</td>
            </tr>`;
        });
        html += '</table>';
    }
    comparacionContenido.innerHTML = html;
}

// FUNCIÓN DE NOTIFICACIÓN 
function mostrarNotificacion(msg) {
    let notif = document.createElement('div');
    notif.className = 'notificacion-exito'; // Asume que tienes este CSS
    notif.innerText = msg;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 2500);
}