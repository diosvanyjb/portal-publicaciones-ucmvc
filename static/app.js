async function cargarPublicaciones() {
    const q = document.getElementById('searchInput').value;
    const res = await fetch(`/api/publicaciones?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    
    const tbody = document.getElementById('tablaBody');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">No hay publicaciones registradas aún. Haz clic en "Cosechar OAI-PMH" para buscar artículos.</td></tr>`;
        return;
    }
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        row.innerHTML = `
            <td class="p-3 font-semibold">${item.autor}</td>
            <td class="p-3"><span class="bg-blue-50 text-blue-800 text-xs px-2 py-1 rounded">${item.categoria} (${item.rol})</span></td>
            <td class="p-3">${item.titulo}</td>
            <td class="p-3 font-medium text-gray-700">${item.revista}</td>
            <td class="p-3">${item.anio} ${item.mes !== 'N/A' ? item.mes : ''}</td>
            <td class="p-3">
                <button onclick="descargarPDF(${item.id}, '${item.url_pdf}')" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-semibold">
                    Descargar PDF
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function descargarPDF(id, url) {
    // Registrar la descarga en la base de datos
    await fetch(`/api/descargar/${id}`, { method: 'POST' });
    
    // Abrir el enlace del PDF oficial
    if (url && url !== '#') {
        window.open(url, '_blank');
    } else {
        alert("Enlace al PDF no disponible en la revista de origen.");
    }
}

async function ejecutarCosecha() {
    alert("Iniciando la recolección OAI-PMH en las revistas de Villa Clara. Por favor, espera unos segundos...");
    const res = await fetch('/api/ejecutar-cosecha');
    const data = await res.json();
    alert(`¡Cosecha completada con éxito! Se han registrado ${data.registros_cosechados} publicaciones.`);
    cargarPublicaciones();
}

// Cargar la lista automáticamente al abrir la página
document.addEventListener('DOMContentLoaded', cargarPublicaciones);