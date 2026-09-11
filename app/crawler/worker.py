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

# Lock compartido entre workers para reclamar URLs de forma atómica (RF4)
lock_reclamo = threading.Lock()


def reclamar_url(session, url_id, worker_id):
    with lock_reclamo:
        url_obj = session.query(Url).get(url_id)
        if url_obj is None or url_obj.estado != "PENDIENTE":
            return None
        url_obj.estado = "EN_PROCESAMIENTO"
        url_obj.worker_id = worker_id
        session.commit()
        return url_obj


def procesar_url(url_id, busqueda_id, persona_id, cola, worker_id):
    session = SessionLocal()
    try:
        url_obj = reclamar_url(session, url_id, worker_id)
        if url_obj is None:
            return

        persona = session.query(Persona).get(persona_id)
        hilo = threading.current_thread().name
        ts = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts}] [{hilo}] → {url_obj.url[:80]}")

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

        # RF5: filtro de contenido relacionado
        relacionado, motivo = es_contenido_relacionado(persona, texto)

        # RF6: persistir documento extraído
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
        session.flush()

        url_obj.estado = "PROCESADA" if relacionado else "DESCARTADA"

        # RF7: verificación de identidad
        if relacionado:
            inicio_analisis = time.time()
            resultado_verificacion = verificar_identidad(persona, texto)
            tiempo_verificacion_ms = int((time.time() - inicio_analisis) * 1000)

            analisis = DocumentoAnalisis(
                documento_id=documento.id,
                verificacion_identidad=resultado_verificacion,
                tiempo_procesamiento_ms=tiempo_verificacion_ms,
            )

            # RF8: clasificación contextual (solo si identidad confirmada o posible)
            if resultado_verificacion in ("MISMA_PERSONA", "POSIBLE_COINCIDENCIA"):
                analisis.clasificacion_contextual = clasificar_contexto(persona, texto)

            session.add(analisis)

        # RF3: descubrir y encolar nuevos enlaces
        if url_obj.profundidad < PROFUNDIDAD_MAXIMA:
            for link in soup.find_all("a", href=True):
                nueva_url = urljoin(url_obj.url, link["href"])
                if urlparse(nueva_url).scheme in ("http", "https"):
                    cola.encolar_url(
                        session, busqueda_id, url_obj.fuente_id,
                        nueva_url, profundidad=url_obj.profundidad + 1
                    )

        url_obj.fecha_procesamiento = datetime.utcnow()
        ts2 = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts2}] [{hilo}] ✓ {url_obj.estado}")
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
