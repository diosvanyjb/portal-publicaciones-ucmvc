document.addEventListener('DOMContentLoaded', () => {
    cargarPublicaciones();
});

async function cargarPublicaciones() {
    const searchInput = document.getElementById('searchInput');
    const q = searchInput ? searchInput.value : '';
    const tbody = document.getElementById('tablaBody');
    
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-blue-600 font-semibold">Cargando publicaciones...</td></tr>`;

    try {
        const res = await fetch(`/api/publicaciones?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        
        tbody.innerHTML = '';

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">No hay publicaciones registradas aún. Haz clic en "Cosechar OAI-PMH" para buscar artículos.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 border-b';
            row.innerHTML = `
                <td class="p-3 font-semibold text-gray-800">${item.autor}</td>
                <td class="p-3"><span class="bg-blue-50 text-blue-800 text-xs px-2 py-1 rounded font-medium">${item.categoria} (${item.rol})</span></td>
                <td class="p-3 text-gray-900 font-medium">${item.titulo}</td>
                <td class="p-3 font-medium text-gray-700">${item.revista}</td>
                <td class="p-3 text-gray-600">${item.anio} ${item.mes && item.mes !== 'N/A' ? item.mes : ''}</td>
                <td class="p-3">
                    <button onclick="descargarPDF(${item.id}, '${item.url_pdf}')" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-xs font-semibold shadow-sm transition-colors">
                        Descargar PDF
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error("Error al cargar publicaciones:", error);
        tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Error al conectar con el servidor. Intenta recargar la página.</td></tr>`;
    }
}

async function descargarPDF(id, url) {
    try {
        await fetch(`/api/descargar/${id}`, { method: 'POST' });
    } catch (e) {
        console.error("Error auditando descarga:", e);
    }
    
    if (url && url !== '#') {
        window.open(url, '_blank');
    } else {
        alert("Enlace al PDF no disponible en la revista de origen.");
    }
}

async function ejecutarCosecha() {
    const tbody = document.getElementById('tablaBody');
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-green-700 font-bold text-lg animate-pulse">🌾 Cosechando artículos de las revistas (EDUMECENTRO y Medicentro)... Por favor espera unos segundos.</td></tr>`;
    }

    try {
        const res = await fetch('/api/ejecutar-cosecha');
        const data = await res.json();
        await cargarPublicaciones();
        alert(`¡Cosecha completada! Se procesaron ${data.registros_cosechados} publicaciones.`);
    } catch (error) {
        console.error("Error durante la cosecha:", error);
        alert("Ocurrió un error al intentar cosechar los artículos.");
        cargarPublicaciones();
    }
}
