import datetime
import io
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd

import database as db
from oai_harvester import REPOSITORIOS_OJS, cosechar_revista

app = FastAPI(title="Portal de Publicaciones UCM Villa Clara")

# Inicializar las tablas de la base de datos al arrancar
db.init_db()

# Configurar carpetas de archivos estáticos y plantillas HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
def home(request: Request):
    """Renderiza la página web principal."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/publicaciones")
def listar_publicaciones(q: str = "", db_session: Session = Depends(get_db)):
    """Obtiene las publicaciones en estricto orden cronológico."""
    query = db_session.query(db.Publicacion).join(db.Autor)
    if q:
        query = query.filter(
            (db.Publicacion.titulo.contains(q)) | 
            (db.Autor.nombre_apellidos.contains(q)) |
            (db.Publicacion.revista.contains(q))
        )
    # Orden descendente por año (las más recientes primero)
    publicaciones = query.order_by(db.Publicacion.anio.desc()).all()
    
    resultado = []
    for p in publicaciones:
        resultado.append({
            "id": p.id,
            "autor": p.autor.nombre_apellidos,
            "categoria": p.autor.categoria_docente,
            "rol": p.autor.rol,
            "titulo": p.titulo,
            "revista": p.revista,
            "anio": p.anio,
            "mes": p.mes,
            "url_pdf": p.url_pdf
        })
    return resultado


@app.post("/api/descargar/{pub_id}")
def registrar_descarga(pub_id: int, db_session: Session = Depends(get_db)):
    """Audita y registra cada evento de descarga en la base de datos."""
    pub = db_session.query(db.Publicacion).filter(db.Publicacion.id == pub_id).first()
    if pub:
        registro = db.RegistroDescarga(publicacion_id=pub.id, fecha_hora=datetime.datetime.utcnow())
        db_session.add(registro)
        db_session.commit()
        return {"status": "ok", "url_pdf": pub.url_pdf}
    return {"status": "error", "message": "Publicación no encontrada"}


@app.get("/api/exportar/excel")
def exportar_excel(db_session: Session = Depends(get_db)):
    """Genera y descarga el archivo Excel consolidado de descargas."""
    descargas = db_session.query(db.RegistroDescarga).join(db.Publicacion).join(db.Autor).all()
    
    data = []
    for d in descargas:
        data.append({
            "Nombre y Apellidos": d.publicacion.autor.nombre_apellidos,
            "Categoría Docente / Rol": f"{d.publicacion.autor.categoria_docente} / {d.publicacion.autor.rol}",
            "Título de la Publicación": d.publicacion.titulo,
            "Revista": d.publicacion.revista,
            "Año": d.publicacion.anio,
            "Mes": d.publicacion.mes,
            "Fecha/Hora de Descarga": d.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Control Descargas')
        
    stream.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="control_descargas.xlsx"'}
    return StreamingResponse(
        stream, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        headers=headers
    )


@app.get("/api/ejecutar-cosecha")
def ejecutar_cosecha(db_session: Session = Depends(get_db)):
    """Ejecuta el bot OAI-PMH en las revistas locales."""
    totales = 0
    for nombre, url in REPOSITORIOS_OJS.items():
        items = cosechar_revista(nombre, url)
        for item in items:
            autor = db_session.query(db.Autor).filter(db.Autor.nombre_apellidos == item["autor_nombre"]).first()
            if not autor:
                autor = db.Autor(
                    nombre_apellidos=item["autor_nombre"], 
                    categoria_docente="Profesor Auxiliar", 
                    rol="Profesor"
                )
                db_session.add(autor)
                db_session.commit()
                db_session.refresh(autor)
                
            pub = db.Publicacion(
                titulo=item["titulo"],
                revista=item["revista"],
                anio=item["anio"],
                mes=item["mes"],
                url_pdf=item["url_pdf"],
                autor_id=autor.id
            )
            db_session.add(pub)
            totales += 1
    db_session.commit()
    return {"status": "Completado", "registros_cosechados": totales}