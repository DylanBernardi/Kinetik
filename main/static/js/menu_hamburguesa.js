document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const mainNav = document.getElementById('mobile-menu');
    const dropdown = document.querySelector('.main-nav .dropdown'); // Seleccionar el <li>.dropdown

    // ----------------------------------------------------
    // Lógica 1: Abrir/Cerrar el Menú Lateral COMPLETO
    // ----------------------------------------------------
    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('open');
            
            const icon = menuToggle.querySelector('i');
            if (mainNav.classList.contains('open')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times'); 
                document.body.style.overflow = 'hidden'; 
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // ----------------------------------------------------
    // Lógica 2: Abrir/Cerrar el Dropdown de "Rutinas"
    // ----------------------------------------------------
    if (dropdown) {
        // Seleccionamos el enlace dentro del li.dropdown (es el primer <a>)
        const dropdownLink = dropdown.querySelector('a');

        // Evitar que el enlace navegue al hacer clic
        dropdownLink.addEventListener('click', function(e) {
            
            // Solo queremos que esto funcione en móvil (cuando el menú lateral está abierto)
            // Si el menú lateral está abierto, asumimos que estamos en vista móvil.
            if (mainNav.classList.contains('open')) {
                e.preventDefault(); // Detener la navegación del enlace (href="#")
                
                // Alternar la clase 'active' en el <li> padre
                dropdown.classList.toggle('active');
            }
        });
    }
});