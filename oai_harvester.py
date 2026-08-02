import re
from typing import List, Dict
from sickle import Sickle

# Direcciones OAI-PMH públicas de las revistas de ciencias médicas
REPOSITORIOS_OJS = {
    "Edumecentro": "http://www.revedumecentro.sld.cu/index.php/edumc/oai",
    "Medicentro Electrónica": "http://www.medicentro.sld.cu/index.php/medicentro/oai",
    "Acta Médica del Centro": "http://www.revactamedicacentro.sld.cu/index.php/amc/oai",
    "CorSalud": "http://www.corsalud.sld.cu/index.php/cors/oai"
}

def cosechar_revista(nombre_revista: str, url_oai: str) -> List[Dict]:
    publicaciones_extraidas = []
    try:
        sickle = Sickle(url_oai)
        records = sickle.ListRecords(metadataPrefix='oai_dc', ignore_deleted=True)
        
        # Limite de prueba por revista para asegurar rapidez inicial
        for idx, record in enumerate(records):
            if idx >= 20: 
                break
            
            metadata = record.metadata
            
            titulo = metadata.get('title', ['Sin título'])[0]
            autores = metadata.get('creator', ['Autor Desconocido'])
            fechas = metadata.get('date', ['N/A'])
            identifiers = metadata.get('identifier', [])
            
            # Buscar el enlace al artículo / PDF
            url_pdf = next((item for item in identifiers if item.startswith("http") and "article" in item), "#")
            
            # Extraer año
            fecha_pub = fechas[0] if fechas else "2026"
            match_anio = re.search(r'\b(19|20)\d{2}\b', fecha_pub)
            anio = int(match_anio.group(0)) if match_anio else 2026
            
            for autor in autores:
                publicaciones_extraidas.append({
                    "autor_nombre": autor,
                    "titulo": titulo,
                    "revista": nombre_revista,
                    "anio": anio,
                    "mes": "N/A",
                    "url_pdf": url_pdf
                })
    except Exception as e:
        print(f"Error cosechando datos de {nombre_revista}: {e}")
        
    return publicaciones_extraidas