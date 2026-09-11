import queue
import threading
from app.models import Url

# Lock compartido para encolar URLs de forma atómica y evitar duplicados (RF4)
lock_encolado = threading.Lock()


class ColaDeUrls:
    """Cola thread-safe de IDs de URLs pendientes de procesar."""

    def __init__(self):
        self._cola = queue.Queue()

    def encolar_url(self, session, busqueda_id, fuente_id, url, profundidad=0):
        with lock_encolado:
            existe = session.query(Url).filter_by(
                busqueda_id=busqueda_id, url=url
            ).first()
            if existe:
                return

            nueva_url = Url(
                busqueda_id=busqueda_id,
                fuente_id=fuente_id,
                url=url,
                estado="PENDIENTE",
                profundidad=profundidad,
            )
            session.add(nueva_url)
            session.commit()
            self._cola.put(nueva_url.id)

    def obtener_url(self, timeout=2):
        try:
            return self._cola.get(timeout=timeout)
        except queue.Empty:
            return None

    def esta_vacia(self):
        return self._cola.empty()
