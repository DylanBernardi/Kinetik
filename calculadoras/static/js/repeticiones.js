document
  .getElementById("rmForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    // Guardamos datos y url
    const peso = document.getElementById("peso").value;
    const reps = document.getElementById("reps").value;
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;
    const ajaxUrl = e.currentTarget.getAttribute("data-ajax-url");

    if (!ajaxUrl) {
      console.error(
        "AJAX URL not found. Check the 'data-ajax-url' attribute on the form."
      );
      return;
    }

    const data = {
      peso: peso,
      reps: reps,
    };

    // Mandamos el AJAX
    try {
      const response = await fetch(ajaxUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      // Procesamos la respuesta
      const resultado = await response.json();

      const tbody = document.querySelector("#rmTable tbody");
      tbody.innerHTML = "";

      // Construimos la tabla
      resultado.table_rows.forEach((row_data) => {
        const row = document.createElement("tr");
        row.innerHTML = `
                <td>${row_data.reps}</td>
                <td>${row_data.peso}</td>
                <td>${row_data.porcentaje}%</td>
            `;

        // Resaltamos la fila correcta
        if (row_data.reps === resultado.input_reps) {
          row.classList.add("current-reps");
        }

        tbody.appendChild(row);
      });
    } catch (error) {
      console.error("Error al calcular:", error);
      document.getElementById(
        "rm-error"
      ).innerHTML = `<p style='color:red;'>Error: ${error.message}</p>`;
    }
  });
