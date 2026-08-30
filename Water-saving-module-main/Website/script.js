const API_URL = "http://127.0.0.1:8000";
 
// Altura total del viewBox de la gota (ver index.html: viewBox="0 0 120 150")
const DROPLET_VIEWBOX_HEIGHT = 150;
 
function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    toast.textContent = mensaje;
    toast.classList.add("show");
 
    clearTimeout(mostrarToast._timeout);
    mostrarToast._timeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}
 
function setEstadoConexion(activo) {
    const badge = document.getElementById("status-badge");
    const text = document.getElementById("status-text");
 
    if (activo) {
        badge.classList.remove("status-offline");
        badge.classList.add("status-active");
        text.textContent = "Sistema activo";
    } else {
        badge.classList.remove("status-active");
        badge.classList.add("status-offline");
        text.textContent = "Desconectado";
    }
}
 
function actualizarHumedad(porcentaje) {
    const pct = Math.max(0, Math.min(100, porcentaje));
    document.getElementById("txt-humedad").innerText = Math.round(pct);
 
    const relleno = document.getElementById("water-level");
    const alturaLlena = (pct / 100) * DROPLET_VIEWBOX_HEIGHT;
    relleno.setAttribute("y", DROPLET_VIEWBOX_HEIGHT - alturaLlena);
    relleno.setAttribute("height", alturaLlena);
}
 
function actualizarTemperatura(valor) {
    document.getElementById("txt-temp").innerText = valor.toFixed(1);
 
    // Escala del termómetro: 0°C a 50°C
    const porcentaje = Math.max(0, Math.min(100, (valor / 50) * 100));
    document.getElementById("bar-temp").style.height = porcentaje + "%";
}
 
async function actualizarDashboard() {
    try {
        const response = await fetch(`${API_URL}/obtener-datos`);
 
        if (!response.ok) {
            throw new Error(`El servidor respondió con estado ${response.status}`);
        }
 
        const data = await response.json();
 
        if (data.error) {
            throw new Error(data.error);
        }
 
        actualizarHumedad(data.humedad);
        actualizarTemperatura(data.temperatura);
        document.getElementById("texto-ia").innerText = `"${data.recomendacion}"`;
 
        setEstadoConexion(true);
    } catch (error) {
        console.error("Error al actualizar el dashboard:", error);
        setEstadoConexion(false);
    }
}
 
function registrarRiego() {
    const input = document.getElementById("input-riego");
    const ml = Number(input.value);
 
    if (!ml || ml <= 0) {
        mostrarToast("Ingresa una cantidad válida en ml.");
        return;
    }
 
    mostrarToast(`Riego de ${ml} ml registrado. ¡Gracias!`);
    input.value = "";
}
 
setInterval(actualizarDashboard, 3000);
actualizarDashboard();