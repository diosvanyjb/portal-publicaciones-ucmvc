import re
from sickle import Sickle

REPOSITORIOS_OJS = {
    "EDUMECENTRO": "https://revedumecentro.sld.cu/index.php/edumc/oai",
    "Medicentro Electrónica": "https://medicentro.sld.cu/index.php/medicentro/oai"
}

MESES_MAP = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
    "jan": "Enero", "feb": "Febrero", "mar": "Marzo", "apr": "Abril",
    "may": "Mayo", "jun": "Junio", "jul": "Julio", "aug": "Agosto",
    "sep": "Septiembre", "oct": "Octubre", "nov": "Noviembre", "dec": "Diciembre"
}


def extraer_anio_y_mes_real(metadata):
    """Extrae el año y mes reales buscando primero en fuentes del volumen y luego en fechas."""
    anio = None
    mes = "Enero"

    # 1. Buscar primero en 'source' (Ej: "EDUMECENTRO 2026; 18(1)" o "Vol. 17 No. 2 (2025)")
    sources = metadata.get("source", [])
    for s in sources:
        s_str = str(s)
        match_anio = re.findall(r'\b(202[0-9]|2030)\b', s_str)
        if match_anio:
            anio = int(match_anio[0])
            break

    # 2. Si no se encontró en 'source', examinar las fechas en orden inverso (la más antigua/original suele estar al final)
    dates = metadata.get("date", [])
    if not anio and dates:
        for d in reversed(dates):
            d_str = str(d)
            match_anio = re.findall(r'\b(202[0-9]|2030)\b', d_str)
            if match_anio:
                anio = int(match_anio[0])

                # Intentar extraer el mes desde el formato AAAA-MM-DD
                match_mes = re.search(r'\d{4}-(\d{2})', d_str)
                if match_mes and match_mes.group(1) in MESES_MAP:
                    mes = MESES_MAP[match_mes.group(1)]
                break

    # 3. Mapear mes si viene escrito en texto dentro del título/source
    texto_completo = " ".join([str(x) for x in sources + dates]).lower()
    for clave_mes, nombre_mes in MESES_MAP.items():
        if clave_mes.isalpha() and clave_mes in texto_completo:
            mes = nombre_mes
            break

    return anio, mes


def cosechar_revista(nombre_revista, url_oai):
    """Cosecha las publicaciones garantizando el año/mes exactos de edición."""
    publicaciones = []
    try:
        sickle = Sickle(url_oai)
        records = sickle.ListRecords(metadataPrefix='oai_dc', ignore_deleted=True)

        for record in records:
            meta = record.metadata
            if not meta:
                continue

            anio, mes = extraer_anio_y_mes_real(meta)

            # Filtrar estrictamente publicaciones entre 2020 y 2030
            if anio and 2020 <= anio <= 2030:
                titulos = meta.get("title", [])
                titulo = titulos[0].strip() if titulos else "Sin título"

                creadores = meta.get("creator", [])
                autor_nombre = creadores[0].strip() if creadores else "Autor Desconocido"

                identificadores = meta.get("identifier", [])
                url_pdf = "#"
                for ident in identificadores:
                    if str(ident).startswith("http") and ("article/view" in str(ident) or "download" in str(ident) or "pdf" in str(ident)):
                        url_pdf = str(ident)
                        break
                if url_pdf == "#" and identificadores:
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
