document.addEventListener("DOMContentLoaded", function () {
  const medidasForm = document.getElementById("medidasForm");
  const comparacionContenido = document.getElementById("comparacionContenido");

  // Función para obtener el CSRF token de Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  if (medidasForm) {
    medidasForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Limpiar errores previos
      document.querySelectorAll(".error-message").forEach((el) => el.remove());

      const formData = new FormData(medidasForm);

      fetch(medidasForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken,
        },
        body: formData,
      })
        .then(async (response) => {
          const data = await response.json();
          if (!response.ok) {
            throw new Error(JSON.stringify(data));
          }
          return data;
        })
        .then((data) => {
          actualizarTablaComparacion(data.data);
          medidasForm.reset(); 
        })
        .catch((errorJson) => {
          const data = JSON.parse(errorJson.message);

          if (data.status === "error" && data.errors) {
            Object.keys(data.errors).forEach((fieldName) => {
              const inputElement = document.getElementById(fieldName);
              if (inputElement) {
                const errorMessage = document.createElement("p");
                errorMessage.className = "error-message";
                errorMessage.textContent = data.errors[fieldName];
                inputElement.parentNode.appendChild(errorMessage);
              }
            });
            mostrarNotificacion(data.message, "error");
          } else {
            mostrarNotificacion(
              data.message || "Error de red. Inténtelo de nuevo.",
              "error"
            );
          }
        });
    });
  }

  function actualizarTablaComparacion(medidas) {
    if (!comparacionContenido) return;

    let html =
      '<table style="width:100%;text-align:center;"><tr><th>Medida</th><th>Anterior</th><th>Actual</th><th>Cambio</th></tr>';

    medidas.forEach((m) => {
      html += `<tr>
                <td>${m.label}</td>
                <td>${m.anterior} cm</td>
                <td>${m.actual} cm</td>
                <td>${m.cambio}</td>
            </tr>`;
    });

    html += "</table>";
    comparacionContenido.innerHTML = html;
  }

});
