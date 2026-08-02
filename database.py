import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Nombre del archivo donde se guardará la base de datos SQLite
DATABASE_URL = "sqlite:///./publicaciones_ucm.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Autor(Base):
    __tablename__ = "autores"
    id = Column(Integer, primary_key=True, index=True)
    nombre_apellidos = Column(String, index=True)
    categoria_docente = Column(String, default="No especificada")
    rol = Column(String, default="Profesor")  # Profesor / Estudiante
    publicaciones = relationship("Publicacion", back_populates="autor")


class Publicacion(Base):
    __tablename__ = "publicaciones"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    revista = Column(String, index=True)
    anio = Column(Integer, index=True)
    mes = Column(String, default="N/A")
    url_pdf = Column(String)
    autor_id = Column(Integer, ForeignKey("autores.id"))
    autor = relationship("Autor", back_populates="publicaciones")
    descargas = relationship("RegistroDescarga", back_populates="publicacion")


class RegistroDescarga(Base):
    __tablename__ = "registros_descargas"
    id = Column(Integer, primary_key=True, index=True)
    publicacion_id = Column(Integer, ForeignKey("publicaciones.id"))
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow)
    publicacion = relationship("Publicacion", back_populates="descargas")


def init_db():
    Base.metadata.create_all(bind=engine)