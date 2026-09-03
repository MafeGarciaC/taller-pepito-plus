"""
Worker del crawler concurrente (RF3, RF4).

Cada worker es una FUNCIÓN que se ejecuta dentro de su propio hilo
(thread). El ThreadPoolExecutor (en app/crawler/__init__.py) se encarga
de crear varios hilos y hacer que cada uno llame a procesar_url() con una
URL distinta. Todos los hilos comparten:
    - la misma ColaDeUrls (para descubrir y encolar enlaces nuevos)
    - el mismo Lock de reclamo (definido abajo)
    - la misma base de datos (aunque cada hilo abre su PROPIA sesión de
      SQLAlchemy -- las sesiones NO se comparten entre hilos, eso sí
      causaría corrupción de datos)
"""

import time
import threading
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app import SessionLocal
from app.models import Url, Documento, DocumentoAnalisis, Persona
from app.services.matching import es_contenido_relacionado
from app.services.identity import verificar_identidad
from app.services.classifier import clasificar_contexto

HEADERS = {"User-Agent": "PepitoPlusBot/1.0 (Taller Sistemas Distribuidos)"}
TIMEOUT_HTTP = 8
PROFUNDIDAD_MAXIMA = 2

# --------------------------------------------------------------------
# CONCEPTO 3: el patrón "reclamar" (claim) con Lock
# --------------------------------------------------------------------
# Este es EXACTAMENTE el requisito RF4: "garantizar que una misma URL no
# sea procesada simultáneamente por más de un worker".
#
# El problema: dos hilos podrían leer el estado de la misma URL ("PENDIENTE")
# al mismo tiempo, y ambos decidir "está libre, la tomo" antes de que
# ninguno alcance a guardar el cambio a "EN_PROCESAMIENTO". Resultado:
# los dos la procesan -> duplicado de trabajo, posible duplicado de datos.
#
# La solución es que LEER el estado actual y CAMBIARLO sea una sola
# operación protegida por Lock ("check-and-set" atómico). Así, mientras
# un hilo está dentro del `with lock_reclamo:`, ningún otro hilo puede
# siquiera leer el estado -- tiene que esperar su turno.
lock_reclamo = threading.Lock()


def reclamar_url(session, url_id, worker_id):
    """
    Intenta tomar una URL para procesarla.
    Devuelve el objeto Url si tuvo éxito, o None si otro worker ya se
    la había quedado (o si ya no está en estado PENDIENTE).
    """
    with lock_reclamo:
        url_obj = session.query(Url).get(url_id)
        if url_obj is None or url_obj.estado != "PENDIENTE":
            return None
        url_obj.estado = "EN_PROCESAMIENTO"
        url_obj.worker_id = worker_id
        session.commit()
        return url_obj


def procesar_url(url_id, busqueda_id, persona_id, cola, worker_id):
    """
    Ciclo de vida completo de una URL:
    reclamar -> descargar -> analizar contenido (RF5) -> persistir (RF6)
    -> descubrir enlaces nuevos -> marcar estado final (RF4)
    """
    session = SessionLocal()
    try:
        url_obj = reclamar_url(session, url_id, worker_id)
        if url_obj is None:
            return  # otro worker se la ganó, o ya fue procesada antes

        persona = session.query(Persona).get(persona_id)

        # --- Descarga de la página ---
        try:
            resp = requests.get(url_obj.url, headers=HEADERS, timeout=TIMEOUT_HTTP)
            resp.raise_for_status()
        except Exception:
            url_obj.estado = "ERROR"
            url_obj.fecha_procesamiento = datetime.utcnow()
            session.commit()
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        texto = soup.get_text(separator=" ", strip=True)
        titulo = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else url_obj.url
        )

        # --- RF5: ¿está relacionado con la persona? ---
        relacionado, motivo = es_contenido_relacionado(persona, texto)

        # --- RF6: persistir el documento extraído ---
        documento = Documento(
            url_id=url_obj.id,
            busqueda_id=busqueda_id,
            titulo=titulo[:500],
            url=url_obj.url,
            fuente_id=url_obj.fuente_id,
            pais=persona.pais,
            contenido_texto=texto[:8000],
            es_relacionado=relacionado,
            motivo_descarte=None if relacionado else motivo,
        )
        session.add(documento)
        session.flush()  # asegura que documento.id ya exista antes de crear el análisis

        url_obj.estado = "PROCESADA" if relacionado else "DESCARTADA"

        # --- RF7: verificación de identidad (solo si pasó el filtro RF5) ---
        if relacionado:
            inicio_analisis = time.time()
            resultado_verificacion = verificar_identidad(persona, texto)
            tiempo_verificacion_ms = int((time.time() - inicio_analisis) * 1000)

            analisis = DocumentoAnalisis(
                documento_id=documento.id,
                verificacion_identidad=resultado_verificacion,
                tiempo_procesamiento_ms=tiempo_verificacion_ms,
            )

            # --- RF8: clasificación contextual ---
            # Solo se analiza el contexto si RF7 confirmó (o casi confirmó)
            # que se trata de la persona; si es PERSONA_DIFERENTE o
            # NO_DETERMINADO, no tiene sentido clasificar un tono que no
            # le corresponde a ella.
            if resultado_verificacion in ("MISMA_PERSONA", "POSIBLE_COINCIDENCIA"):
                analisis.clasificacion_contextual = clasificar_contexto(persona, texto)

            session.add(analisis)

        # --- RF3: descubrir enlaces nuevos y encolarlos ---
        if url_obj.profundidad < PROFUNDIDAD_MAXIMA:
            for link in soup.find_all("a", href=True):
                nueva_url = urljoin(url_obj.url, link["href"])
                if urlparse(nueva_url).scheme in ("http", "https"):
                    cola.encolar_url(
                        session, busqueda_id, url_obj.fuente_id,
                        nueva_url, profundidad=url_obj.profundidad + 1
                    )

        url_obj.fecha_procesamiento = datetime.utcnow()
        session.commit()

    except Exception:
        session.rollback()
        try:
            url_obj = session.query(Url).get(url_id)
            if url_obj:
                url_obj.estado = "ERROR"
                session.commit()
        except Exception:
            pass
    finally:
        session.close()