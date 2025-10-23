document
  .getElementById("mrForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    //Conseguimos los datos del form
    const peso = document.getElementById("peso").value;
    const edad = document.getElementById("edad").value;
    const sexo = document.getElementById("sexo").value;
    const actividad = document.getElementById("actividad").value;
    const objetivo = document.getElementById("objetivo").value;

    //Validacion simple
    if (!peso || !edad || !sexo || !actividad || !objetivo) {
      document.getElementById("resultado").innerHTML =
        "<p style='color:red;'>Por favor, completa todos los campos.</p>";
      return;
    }

    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    //Conseguimos la URL del AJAX desde el atributo data-ajax-url del form
    const ajaxUrl = e.currentTarget.getAttribute("data-ajax-url");

    if (!ajaxUrl) {
      console.error(
        "AJAX URL not found. Check the 'data-ajax-url' attribute on the form."
      );
      return;
    }

    //Datos para el AJAX
    const data = {
      peso: peso,
      edad: edad,
      sexo: sexo,
      actividad: actividad,
      objetivo: objetivo,
    };

    //Mandamos el AJAX
    try {
      const response = await fetch(ajaxUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken, // Include the CSRF token
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      //Procesamos el Json
      const resultado = await response.json();

      //Mostramos resultados
      let objetivoTexto = "";
      if (resultado.objetivo === "mantener") {
        objetivoTexto = "mantener tu peso";
      } else if (resultado.objetivo === "bajar") {
        objetivoTexto = "bajar de peso";
      } else {
        objetivoTexto = "subir de peso";
      }

      document.getElementById("resultado").innerHTML = `
                <h3>Resultado:</h3>
                <p>Tu requerimiento calórico diario estimado es: <strong>${resultado.calorias_totales} kcal</strong></p>
                <p>Para <strong>${objetivoTexto}</strong>.</p>
                <h4>Distribución de macronutrientes:</h4>
                <ul style="list-style:none;padding:0;">
                    <li><strong>Proteínas:</strong> ${resultado.proteinas_gr}g (${resultado.proteinas_porcentaje}%)</li>
                    <li><strong>Grasas:</strong> ${resultado.grasas_gr}g (${resultado.grasas_porcentaje}%)</li>
                    <li><strong>Carbohidratos:</strong> ${resultado.carbohidratos_gr}g (${resultado.carbohidratos_porcentaje}%)</li>
                </ul>
            `;
    } catch (error) {
      console.error("Error al calcular:", error);
      document.getElementById(
        "resultado"
      ).innerHTML = `<p style='color:red;'>Ocurrió un error en el cálculo: ${error.message}</p>`;
    }
  });
