from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
 
Base = declarative_base()
 
 
# ============================================================
# 1. PERSONAS (RF1)
# ============================================================
class Persona(Base):
    __tablename__ = "personas"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(255), nullable=False)
    pais = Column(String(100), nullable=False)
    ciudad = Column(String(100))
    profesion_cargo = Column(String(150))
    empresa_organizacion = Column(String(150))
    alias = Column(String(255))
    palabras_relacionadas = Column(Text)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
 
    busquedas = relationship("Busqueda", back_populates="persona", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Persona {self.nombre_completo} ({self.pais})>"
 
 
# ============================================================
# 2. FUENTES (RF2)
# ============================================================
class Fuente(Base):
    __tablename__ = "fuentes"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    url_inicial = Column(String(500), nullable=False)
    pais = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    estado = Column(Enum("ACTIVA", "INACTIVA", name="estado_fuente"), default="ACTIVA", nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
 
    urls = relationship("Url", back_populates="fuente")
    documentos = relationship("Documento", back_populates="fuente")
 
    def __repr__(self):
        return f"<Fuente {self.nombre} ({self.pais})>"
 
 
# ============================================================
# 3. BUSQUEDAS
# ============================================================
class Busqueda(Base):
    __tablename__ = "busquedas"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    persona_id = Column(Integer, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    pais = Column(String(100), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(
        Enum("EN_PROGRESO", "COMPLETADA", "ERROR", name="estado_busqueda"),
        default="EN_PROGRESO", nullable=False
    )
    num_workers = Column(Integer, default=1)
 
    persona = relationship("Persona", back_populates="busquedas")
    urls = relationship("Url", back_populates="busqueda", cascade="all, delete-orphan")
    documentos = relationship("Documento", back_populates="busqueda", cascade="all, delete-orphan")
    metricas = relationship("MetricaConcurrencia", back_populates="busqueda", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Busqueda id={self.id} persona_id={self.persona_id} estado={self.estado}>"
 
 
# ============================================================
# 4. URLS (RF3, RF4)
# ============================================================
class Url(Base):
    __tablename__ = "urls"
    __table_args__ = (
        UniqueConstraint("busqueda_id", "url", name="uq_url_busqueda"),
    )
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    busqueda_id = Column(Integer, ForeignKey("busquedas.id", ondelete="CASCADE"), nullable=False)
    fuente_id = Column(Integer, ForeignKey("fuentes.id"), nullable=False)
    url = Column(String(1000), nullable=False)
    estado = Column(
        Enum("PENDIENTE", "EN_PROCESAMIENTO", "PROCESADA", "DESCARTADA", "ERROR", name="estado_url"),
        default="PENDIENTE", nullable=False
    )
    profundidad = Column(Integer, default=0)
    fecha_descubrimiento = Column(DateTime, default=datetime.utcnow)
    fecha_procesamiento = Column(DateTime, nullable=True)
    worker_id = Column(String(50), nullable=True)
 
    busqueda = relationship("Busqueda", back_populates="urls")
    fuente = relationship("Fuente", back_populates="urls")
    documento = relationship("Documento", back_populates="url_origen", uselist=False)
 
    def __repr__(self):
        return f"<Url id={self.id} estado={self.estado} url={self.url[:50]}>"
 
 
# ============================================================
# 5. DOCUMENTOS (RF5, RF6)
# ============================================================
class Documento(Base):
    __tablename__ = "documentos"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)
    busqueda_id = Column(Integer, ForeignKey("busquedas.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(500))
    url = Column(String(1000), nullable=False)
    fuente_id = Column(Integer, ForeignKey("fuentes.id"), nullable=False)
    pais = Column(String(100))
    fecha_publicacion = Column(Date, nullable=True)
    fecha_consulta = Column(DateTime, default=datetime.utcnow)
    contenido_texto = Column(Text)
    es_relacionado = Column(Boolean, default=False, nullable=False)
    motivo_descarte = Column(String(255), nullable=True)
 
    url_origen = relationship("Url", back_populates="documento")
    busqueda = relationship("Busqueda", back_populates="documentos")
    fuente = relationship("Fuente", back_populates="documentos")
    analisis = relationship("DocumentoAnalisis", back_populates="documento", uselist=False, cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Documento id={self.id} titulo={self.titulo[:40] if self.titulo else None}>"
 
 
# ============================================================
# 6. DOCUMENTO_ANALISIS (RF7, RF8)
# ============================================================
class DocumentoAnalisis(Base):
    __tablename__ = "documento_analisis"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False, unique=True)
    verificacion_identidad = Column(
        Enum("MISMA_PERSONA", "POSIBLE_COINCIDENCIA", "PERSONA_DIFERENTE", "NO_DETERMINADO",
             name="verificacion_identidad_enum"),
        nullable=False
    )
    clasificacion_contextual = Column(
        Enum("POSITIVO", "NEUTRO", "NEGATIVO", "NO_DETERMINADO", name="clasificacion_contextual_enum"),
        nullable=True
    )
    fecha_analisis = Column(DateTime, default=datetime.utcnow)
    tiempo_procesamiento_ms = Column(Integer, nullable=True)
 
    documento = relationship("Documento", back_populates="analisis")
 
    def __repr__(self):
        return f"<DocumentoAnalisis documento_id={self.documento_id} verif={self.verificacion_identidad}>"
 
 
# ============================================================
# 7. METRICAS_CONCURRENCIA
# ============================================================
class MetricaConcurrencia(Base):
    __tablename__ = "metricas_concurrencia"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    busqueda_id = Column(Integer, ForeignKey("busquedas.id", ondelete="CASCADE"), nullable=False)
    fase = Column(
        Enum("CRAWLING", "MATCHING", "VERIFICACION", "CLASIFICACION", name="fase_metrica"),
        nullable=False
    )
    num_workers = Column(Integer, nullable=False)
    tiempo_total_ms = Column(Integer, nullable=False)
    elementos_procesados = Column(Integer, nullable=False)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow)
 
    busqueda = relationship("Busqueda", back_populates="metricas")
 
    def __repr__(self):
        return f"<MetricaConcurrencia fase={self.fase} workers={self.num_workers} tiempo_ms={self.tiempo_total_ms}>"
 