let ejerciciosData = [];

document.addEventListener("DOMContentLoaded", function () {

    const dataElement = document.getElementById("ejercicios-data");
    if (dataElement) {
        try {
            ejerciciosData = JSON.parse(dataElement.textContent.trim());
        } catch (e) {
            console.error("Error al cargar los datos", e);
        }
    }
  

    // 1. Asignar los listeners a los botones "Añadir Ejercicio"
    document.querySelectorAll(".btn-add-ejercicio").forEach((button) => {
        button.addEventListener("click", function () {
            agregarFila(this.getAttribute("data-dia-num"));
        });
    });

    // 2. Asignar listeners a los botones de eliminar existentes (y manejo de orden)
    document.querySelectorAll(".btn-eliminar").forEach((button) => {
        button.onclick = function () {
            const tbody = this.closest("tbody");
            this.closest("tr").remove();
            updateOrder(tbody); // 🚨 Actualizar orden al eliminar
        };
    });

    // 3. Inicializar el orden de las tablas existentes (modo Edición)
    document.querySelectorAll(".tabla-ejercicios tbody").forEach((tbody) => {
        updateOrder(tbody);
    });
});



function updateOrder(tablaBody) {
    let order = 1;
    // Iteramos sobre todas las filas (tr) dentro del tbody
    tablaBody.querySelectorAll("tr").forEach((row) => {
        // Buscamos la celda con la clase '.orden-celda'
        const orderCell = row.querySelector(".orden-celda"); 
        
        if (orderCell) {
            orderCell.textContent = order;
        }
        order++;
    });
}


// Función auxiliar para generar el HTML del <select> de ejercicios
function crearSelectEjercicioHTML(diaNum) {
    let options = '<option value="">--- Seleccionar Ejercicio ---</option>';
    ejerciciosData.forEach((ej) => {
        options += `<option value="${ej.id}">${ej.nombre}</option>`; 
    });
    return `<select name="dia_${diaNum}_ejercicio[]" required>${options}</select>`;
}

function agregarFila(diaNum) {
    const tablaBody = document
        .getElementById(`tabla-dia-${diaNum}`)
        .getElementsByTagName("tbody")[0];
    let nuevaFila;

    if (tablaBody.rows.length === 0) {
        const selectHtml = crearSelectEjercicioHTML(diaNum);

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${selectHtml}</td>
            <td><input placeholder="Series" type="number" min="1" name="dia_${diaNum}_series[]" required></td>
            <td><input placeholder="Repeticiones" type="number" min="1" name="dia_${diaNum}_repeticiones[]" required></td>
            <td><input placeholder="Peso" type="number" step="0.5" min="0" name="dia_${diaNum}_peso[]"></td>
            <td><input placeholder="Descanso" type="number" min="0" name="dia_${diaNum}_descanso[]" required></td>
            <td><button type="button" class="btn-eliminar">Eliminar</button></td>
        `;
        nuevaFila = tr;
    } else {
        const filaBase = tablaBody.rows[tablaBody.rows.length - 1];
        nuevaFila = filaBase.cloneNode(true);

        nuevaFila.querySelectorAll("input, select").forEach((input) => {
            input.value = "";
            if (input.tagName === "SELECT") {
                input.selectedIndex = 0;
            }
            // Importante: limpiamos el atributo selected en las opciones clonadas
            if (input.tagName === "SELECT") {
                input.querySelectorAll('option[selected]').forEach(opt => opt.removeAttribute('selected'));
            }
        });
    }

    // Listener de eliminación
    let removeButton = nuevaFila.querySelector(".btn-eliminar");
    if (removeButton) {
        removeButton.onclick = function () {
            const tbody = this.closest("tbody");
            this.closest("tr").remove();
            updateOrder(tbody);
        };
    }

    tablaBody.appendChild(nuevaFila);
    updateOrder(tablaBody); 
}

