// rutinas_app/static/js/rutina.js

let ejerciciosData = [];

// Función auxiliar para generar el HTML del <select> de ejercicios
function crearSelectEjercicioHTML(diaNum) {
  let options = '<option value="">--- Seleccionar Ejercicio ---</option>';
  ejerciciosData.forEach((ej) => {
    options += `<option value="${ej.id}">${ej.nombre}</option>`;
  });
  // Devuelve el HTML del select completo
  return `<select name="dia_${diaNum}_ejercicio[]" required>${options}</select>`;
}

// ----------------------------------------------------
// FUNCIÓN PRINCIPAL: Añadir/Clonar Fila
// ----------------------------------------------------
function agregarFila(diaNum) {
  const tablaBody = document
    .getElementById(`tabla-dia-${diaNum}`)
    .getElementsByTagName("tbody")[0];
  let nuevaFila;

  // 🚨 CASO 1: NO HAY FILAS (Modo Creación o Día vacío en Edición)
  if (tablaBody.rows.length === 0) {
    const selectHtml = crearSelectEjercicioHTML(diaNum);

    // Creamos la fila completa desde una string de HTML
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${selectHtml}</td>
            <td><input type="number" step="0.5" min="0" name="dia_${diaNum}_peso[]"></td>
            <td><input type="number" min="1" name="dia_${diaNum}_repeticiones[]" required></td>
            <td><input type="number" min="1" name="dia_${diaNum}_series[]" required></td>
            <td><input type="number" min="0" name="dia_${diaNum}_descanso[]" required></td>
            <td><button type="button" class="btn-eliminar">Eliminar</button></td>
        `;
    nuevaFila = tr;
  } else {
    // 🚨 CASO 2: YA HAY FILAS (Clonamos la última para mantener consistencia)
    const filaBase = tablaBody.rows[tablaBody.rows.length - 1];
    nuevaFila = filaBase.cloneNode(true);

    // Limpiar los valores (aplica a la clonación)
    nuevaFila.querySelectorAll("input, select").forEach((input) => {
      input.value = "";
      if (input.tagName === "SELECT") {
        input.selectedIndex = 0; // Selecciona la opción por defecto
        input.removeAttribute("selected"); // Importante para la edición
      }
    });
  }

  // 3. Asignar el listener de eliminar (Aplica a ambos casos)
  let removeButton = nuevaFila.querySelector(".btn-eliminar");
  if (removeButton) {
    removeButton.onclick = function () {
      this.closest("tr").remove();
    };
  }

  tablaBody.appendChild(nuevaFila);
}

// ----------------------------------------------------
// INICIALIZACIÓN (Se ejecuta al cargar la página)
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  // Cargar los datos de ejercicios desde la etiqueta <script> JSON
  const dataElement = document.getElementById("ejercicios-data");
  if (dataElement) {
    try {
      ejerciciosData = JSON.parse(dataElement.textContent);
    } catch (e) {
      console.error("Error al parsear datos de ejercicios:", e);
    }
  }

  // 1. Asignar los listeners a los botones "Añadir Ejercicio"

  document.querySelectorAll(".btn-add-ejercicio").forEach((button) => {
    button.addEventListener("click", function () {
      agregarFila(this.getAttribute("data-dia-num"));
    });
  });

  // 2. Asignar listeners a los botones de eliminar existentes (útil para el modo Edición)
  document.querySelectorAll(".btn-eliminar").forEach((button) => {
    button.onclick = function () {
      this.closest("tr").remove();
    };
  });
});
