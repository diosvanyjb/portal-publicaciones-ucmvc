import re
from sickle import Sickle

REPOSITORIOS_OJS = {
    "EDUMECENTRO": "https://revedumecentro.sld.cu/index.php/edumc/oai",
    "Medicentro Electrónica": "https://medicentro.sld.cu/index.php/medicentro/oai"
}

def extraer_anio_y_mes(metadata):
    """Extrae cualquier año entre 2020 y 2030 presente en los metadatos."""
    dates = metadata.get("date", [])
    anio = None
    mes = "Enero"

    meses_map = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    # Buscar exhaustivamente cualquier año de 4 dígitos entre 2020 y 2030
    for d in dates:
        d_str = str(d)
        coincidencias = re.findall(r'\b(202[0-9]|2030)\b', d_str)
        if coincidencias:
            anio = int(coincidencias[0])
            
            # Buscar el mes si viene en formato AAAA-MM-DD
            match_mes = re.search(r'\d{4}-(\d{2})', d_str)
            if match_mes and match_mes.group(1) in meses_map:
                mes = meses_map[match_mes.group(1)]
            break

    return anio, mes


def cosechar_revista(nombre_revista, url_oai):
    """Cosecha y filtra publicaciones dentro del rango 2020-2030."""
    publicaciones = []
    try:
        sickle = Sickle(url_oai)
        records = sickle.ListRecords(metadataPrefix='oai_dc', ignore_deleted=True)

        for record in records:
            meta = record.metadata
            if not meta:
                continue

            anio, mes = extraer_anio_y_mes(meta)

            # Guardar SOLO si se encontró un año válido entre 2020 y 2030
            if anio and 2020 <= anio <= 2030:
                titulos = meta.get("title", [])
                titulo = titulos[0].strip() if titulos else "Sin título"

                creadores = meta.get("creator", [])
                autor_nombre = creadores[0].strip() if creadores else "Autor Desconocido"

                identificadores = meta.get("identifier", [])
                url_pdf = "#"
                for ident in identificadores:
                    if str(ident).startswith("http"):
                        url_pdf = str(ident)
                        break

                publicaciones.append({
                    "titulo": titulo,
                    "autor_nombre": autor_nombre,
                    "revista": nombre_revista,
                    "anio": anio,
                    "mes": mes,
                    "url_pdf": url_pdf
                })

    except Exception as e:
        print(f"Error al cosechar {nombre_revista}: {e}")

    return publicaciones
