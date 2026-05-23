let jugadores = [];
let jugadorActual = null;
let rachaActual = 0;

// Lista de equipos para generar opciones falsas rápidamente
const TODOS_LOS_EQUIPOS = [
    "Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors",
    "Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks",
    "Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards",
    "Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz",
    "Golden State Warriors", "Los Angeles Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings",
    "Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"
];

// 1. Cargar el JSON generado por Python
async function cargarJugadores() {
    try {
        const respuesta = await fetch('jugadores_nba.json');
        jugadores = await respuesta.json();
        if(jugadores.length > 0) {
            siguientePregunta();
        } else {
            document.getElementById('jugador-nombre').innerText = "JSON vacío. Espera a que Python termine.";
        }
    } catch (error) {
        console.error("Error cargando el JSON:", error);
        document.getElementById('jugador-nombre').innerText = "Error al cargar datos. ¿Ejecutaste el script?";
    }
}

// 2. Seleccionar jugador y montar la botonera
function siguientePregunta() {
    // Resetear interfaz
    document.getElementById('stats-contenedor').classList.add('hidden');
    document.getElementById('btn-siguiente').classList.add('hidden');
    
    // Resetear el texto de la temporada para el nuevo jugador
    document.getElementById('jugador-temporada').innerText = "—";
    
    // Elegir jugador aleatorio
    jugadorActual = jugadores[Math.floor(Math.random() * jugadores.length)];
    
    // Actualizar Tarjeta
    document.getElementById('jugador-nombre').innerText = jugadorActual.nombre;
    document.getElementById('jugador-foto').src = jugadorActual.foto;
    
    // Generar opciones (1 correcta + 3 falsas)
    let opciones = [jugadorActual.equipo];
    while(opciones.length < 4) {
        let equipoAleatorio = TODOS_LOS_EQUIPOS[Math.floor(Math.random() * TODOS_LOS_EQUIPOS.length)];
        if(!opciones.includes(equipoAleatorio)) {
            opciones.push(equipoAleatorio);
        }
    }
    // Barajar las opciones para que la correcta no sea siempre la primera
    opciones.sort(() => Math.random() - 0.5);
    
    // Pintar botones
    const container = document.getElementById('opciones-container');
    container.innerHTML = ''; // Limpiar anteriores
    
    opciones.forEach(equipo => {
        const btn = document.createElement('button');
        btn.innerText = equipo;
        btn.className = "bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-700 rounded-xl p-3 text-sm font-semibold transition duration-150 transform active:scale-95 text-center break-words";
        btn.onclick = () => verificarRespuesta(btn, equipo);
        container.appendChild(btn);
    });
}

// 3. Verificar si acertó
function verificarRespuesta(botonSeleccionado, equipoSeleccionado) {
    const botones = document.getElementById('opciones-container').children;
    
    // Deshabilitar todos los botones para que no sigan clickeando
    for (let btn of botones) {
        btn.disabled = true;
        // Pintar el correcto de verde por si acaso
        if (btn.innerText === jugadorActual.equipo) {
            btn.className = "bg-green-600 border-green-500 text-white rounded-xl p-3 text-sm font-bold text-center break-words";
        }
    }
    
    if (equipoSeleccionado === jugadorActual.equipo) {
        rachaActual++;
    } else {
        // Si falló, pintamos su selección de rojo
        botonSeleccionado.className = "bg-red-600 border-red-500 text-white rounded-xl p-3 text-sm font-bold text-center break-words";
        rachaActual = 0; // Se rompe la racha
    }
    
    // Actualizar marcador de racha
    document.getElementById('racha').innerText = rachaActual;
    
    // Mostrar la temporada de los datos en el elemento HTML
    if (jugadorActual.temporada) {
        document.getElementById('jugador-temporada').innerText = `STATS TEMP. ${jugadorActual.temporada}`;
    } else {
        document.getElementById('jugador-temporada').innerText = "STATS DISPONIBLES";
    }
    
    // Mostrar estadísticas del jugador
    document.getElementById('stat-pos').innerText = jugadorActual.posicion;
    document.getElementById('stat-pts').innerText = jugadorActual.stats.PTS;
    document.getElementById('stat-reb').innerText = jugadorActual.stats.REB;
    document.getElementById('stat-ast').innerText = jugadorActual.stats.AST;
    document.getElementById('stats-contenedor').classList.remove('hidden');
    
    // Mostrar botón de siguiente
    document.getElementById('btn-siguiente').classList.remove('hidden');
}

// Configurar el botón de siguiente
document.getElementById('btn-siguiente').onclick = siguientePregunta;

// Iniciar el juego al cargar la página
window.onload = cargarJugadores;