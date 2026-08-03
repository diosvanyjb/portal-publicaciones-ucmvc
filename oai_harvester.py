import re
from sickle import Sickle

# URLs de los repositorios OJS a cosechar
REPOSITORIOS_OJS = {
    "EDUMECENTRO": "https://revedumecentro.sld.cu/index.php/edumc/oai",
    "Medicentro Electrónica": "https://medicentro.sld.cu/index.php/medicentro/oai"
}

def extraer_anio_y_mes(metadata):
    """Extrae el año (entre 2020 y 2030) y el mes desde los metadatos OAI-PMH."""
    dates = metadata.get("date", [])
    anio = 2024  # Valor por defecto si no se encuentra
    mes = "Enero"

    # Buscar un año de 4 dígitos entre 2020 y 2030 en todas las fechas disponibles
    for d in dates:
        coincidencias = re.findall(r'\b(202[0-9]|2030)\b', str(d))
        if coincidencias:
            anio = int(coincidencias[0])
            break

    # Diccionario de meses para mapear fechas en texto o número
    meses_map = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    for d in dates:
        d_str = str(d).lower()
        # Intentar extraer mes en formato AAAA-MM-DD
        match_mes = re.search(r'\d{4}-(\d{2})', d_str)
        if match_mes and match_mes.group(1) in meses_map:
            mes = meses_map[match_mes.group(1)]
            break

    return anio, mes


def cosechar_revista(nombre_revista, url_oai):
    """Conecta al servidor OAI-PMH de la revista y extrae las publicaciones."""
    publicaciones = []
    try:
        sickle = Sickle(url_oai)
        records = sickle.ListRecords(metadataPrefix='oai_dc', ignore_deleted=True)

        for record in records:
            meta = record.metadata
            if not meta:
                continue

            # Extraer título
            titulos = meta.get("title", [])
            titulo = titulos[0].strip() if titulos else "Sin título"

            # Extraer autor principal
            creadores = meta.get("creator", [])
            autor_nombre = creadores[0].strip() if creadores else "Autor Desconocido"

            # Extraer enlace al PDF o artículo
            identificadores = meta.get("identifier", [])
            url_pdf = "#"
            for ident in identificadores:
                if str(ident).startswith("http"):
                    url_pdf = str(ident)
                    break

            # Extraer año y mes soportando rango 2020-2030
            anio, mes = extraer_anio_y_mes(meta)

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
