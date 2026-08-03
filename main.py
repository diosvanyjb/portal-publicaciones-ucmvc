@app.get("/api/publicaciones")
def listar_publicaciones(q: str = "", db_session: Session = Depends(get_db)):
    """Obtiene todas las publicaciones ordenadas por año descendente."""
    query = db_session.query(db.Publicacion).join(db.Autor)
    
    if q:
        query = query.filter(
            (db.Publicacion.titulo.contains(q)) | 
            (db.Autor.nombre_apellidos.contains(q)) |
            (db.Publicacion.revista.contains(q))
        )
    # Muestra de mayor a menor año (2026, 2025, 2024, etc.)
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
