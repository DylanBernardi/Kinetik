document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const routineSection = document.getElementById('routineSection');
    let calendarInstance;

    function initializeCalendar() {
        calendarInstance = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            height: 'auto',
            headerToolbar: false,
            locale: 'es',
            editable: false,
            selectable: true,
            fixedWeekCount: false,
            showNonCurrentDates: false,
            events: fetchProgrammedRoutines,
            eventClick: function(info) {
                const routineId = info.event.id;
                const dayIndex = info.event.extendedProps.dayIndex;
                showRoutineForDate(routineId, dayIndex);
            },
            dateClick: function(info) {
                const eventOnDate = calendarInstance.getEvents().find(e => e.startStr.split('T')[0] === info.dateStr);
                if (eventOnDate) {
                    const routineId = eventOnDate.id;
                    const dayIndex = eventOnDate.extendedProps.dayIndex;
                    showRoutineForDate(routineId, dayIndex);
                } else {
                    displayNoRoutine(info.dateStr);
                }
            },
        });

        calendarInstance.render();
        setupCustomNavigation();
        updateRoutineViewForToday();
    }

    async function fetchProgrammedRoutines(fetchInfo, successCallback, failureCallback) {
        try {
            const response = await fetch('http://localhost/Tp_Final_Interfaces/backend/api/rutinas/obtener_rutinas_programadas.php', {
                credentials: 'include'
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const events = await response.json();
            successCallback(events);
        } catch (error) {
            console.error('Error fetching programmed routines:', error);
            failureCallback(error);
        }
    }

    async function showRoutineForDate(routineId, dayIndex) {
        if (!routineId) {
            displayNoRoutine(new Date().toISOString().split('T')[0]);
            return;
        }
        try {
            const response = await fetch(`https://myproyectTPinterfaces.infy.uk/backend/api/rutinas/obtener_rutinas.php?id=${routineId}`, {
                credentials: 'include'
            });
            if (!response.ok) throw new Error('Failed to fetch routine details');
            
            const result = await response.json();
            if (result.success) {
                displayRoutineDay(result.rutina, dayIndex);
            } else {
                displayNoRoutine(new Date().toISOString().split('T')[0], result.mensaje);
            }
        } catch (error) {
            console.error('Error fetching routine details:', error);
            displayNoRoutine(new Date().toISOString().split('T')[0], 'Error al cargar la rutina.');
        }
    }

    function displayRoutineDay(routine, dayIndex) {
    const dayData = routine.days[dayIndex];
    if (!dayData) {
        routineSection.innerHTML = `<h2>Rutina de Hoy</h2><p>No hay datos para este día.</p>`;
        return;
    }

    // Eliminar ejercicios duplicados
    const ejerciciosUnicos = [...new Set(dayData.exercises)];

    let exercisesHtml = ejerciciosUnicos.map(ex => `<li>${ex}</li>`).join('');

    routineSection.innerHTML = `
        <h2>Rutina de Hoy</h2>
        <div class="rutina-hoy">
            <div class="rutina-card ${routine.tipo || ''}">
                <div class="rutina-header">
                    <i class="fas fa-${(routine.tipo || 'casa') === 'gimnasio' ? 'dumbbell' : 'home'}"></i>
                    <h3>${routine.title}</h3>
                </div>
                <h4>${dayData.name}</h4>
                <ul class="exercise-list-detailed">
                    ${exercisesHtml}
                </ul>
            </div>
        </div>
    `;
}
    function displayNoRoutine(dateStr, message = 'No hay rutina programada') {
        const formattedDate = new Date(dateStr + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
        routineSection.innerHTML = `
            <h2>Rutina para ${formattedDate}</h2>
            <div class="no-rutina">
                <i class="fas fa-calendar-plus"></i>
                <p>${message}</p>
                <button class="btn-crear-rutina" onclick="window.location.href='crear_rutina.html?fecha=${dateStr}'">
                    <i class="fas fa-plus"></i> Crear Rutina Personalizada
                </button>
            </div>
        `;
    }

    function updateRoutineViewForToday() {
        const todayStr = new Date().toISOString().split('T')[0];
        const eventOnDate = calendarInstance.getEvents().find(e => e.startStr.split('T')[0] === todayStr);
        if (eventOnDate) {
            const routineId = eventOnDate.id;
            const dayIndex = eventOnDate.extendedProps.dayIndex;
            showRoutineForDate(routineId, dayIndex);
        } else {
            // Wait for events to load
            setTimeout(() => {
                const eventOnDate = calendarInstance.getEvents().find(e => e.startStr.split('T')[0] === todayStr);
                 if (eventOnDate) {
                    const routineId = eventOnDate.id;
                    const dayIndex = eventOnDate.extendedProps.dayIndex;
                    showRoutineForDate(routineId, dayIndex);
                } else {
                    displayNoRoutine(todayStr);
                }
            }, 1000); // wait 1 sec for events to fetch
        }
    }

    function setupCustomNavigation() {
        const navContainer = document.createElement('div');
        navContainer.className = 'calendar-nav';
        
        const navControls = document.createElement('div');
        navControls.className = 'nav-controls';
        
        const prevBtn = document.createElement('button');
        prevBtn.innerHTML = '←';
        prevBtn.onclick = () => {
            calendarInstance.prev();
            updateTitle();
        };
        
        const monthTitle = document.createElement('div');
        monthTitle.className = 'month-title';
        
        const nextBtn = document.createElement('button');
        nextBtn.innerHTML = '→';
        nextBtn.onclick = () => {
            calendarInstance.next();
            updateTitle();
        };
        
        const todayBtn = document.createElement('button');
        todayBtn.className = 'today-button';
        todayBtn.innerHTML = 'Día Actual';
        todayBtn.onclick = () => {
            calendarInstance.today();
            updateTitle();
        };
        
        function updateTitle() {
            const date = calendarInstance.getDate();
            monthTitle.innerHTML = date.toLocaleDateString('es', { month: 'long', year: 'numeric' });
        }
        
        updateTitle();
        
        navControls.appendChild(prevBtn);
        navControls.appendChild(monthTitle);
        navControls.appendChild(nextBtn);
        
        navContainer.appendChild(navControls);
        navContainer.appendChild(todayBtn);
        
        calendarEl.insertBefore(navContainer, calendarEl.firstChild);
    }

    initializeCalendar();
    function inicializarBotonBorrarTodas() {
    const btn = document.getElementById('btnBorrarTodasRutinas');
    if (!btn) return;

    btn.onclick = async function() {
        const confirmar = confirm('¿Seguro que quieres borrar TODAS las rutinas programadas? Esta acción no se puede deshacer.');
        if (!confirmar) return;

        try {
            const response = await fetch('http://localhost/TP_FINAL_INTERFACES/backend/api/rutinas/borrar_todas_rutinas.php', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                alert('✅ Todas las rutinas programadas fueron borradas.');
                location.reload();
            } else {
                alert('❌ Error: ' + (result.mensaje || 'No se pudieron borrar las rutinas.'));
            }
        } catch (e) {
            alert('❌ Error de conexión con el servidor.');
        }
    };
}

// Llama a esta función después de initializeCalendar();
inicializarBotonBorrarTodas();
});