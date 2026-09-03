"""
Cola compartida de URLs para el crawler concurrente (RF3, RF4).

--------------------------------------------------------------------
CONCEPTO 1: queue.Queue
--------------------------------------------------------------------
Es una lista especial diseñada para que MÚLTIPLES HILOS (threads) puedan
sacar y meter elementos al mismo tiempo sin corromper los datos. Por
dentro ya usa sus propios candados, así que put() y get() son "thread-safe"
sin que tengamos que hacer nada extra. Es la estructura ideal para repartir
trabajo: un hilo mete URLs, y varios hilos las van sacando para procesarlas.

--------------------------------------------------------------------
CONCEPTO 2: threading.Lock (candado)
--------------------------------------------------------------------
Un Lock es literalmente un candado: solo un hilo a la vez puede tener la
llave (usando `with lock:`). Los demás hilos que intenten entrar a ese
bloque de código se quedan ESPERANDO en fila hasta que el primero salga.

¿Por qué lo necesitamos aquí si queue.Queue ya es segura? Porque insertar
una URL nueva implica DOS pasos que deben pasar juntos, como una sola
operación indivisible ("atómica"):
    (a) revisar en la base de datos si esa URL ya existe para esta búsqueda
    (b) si no existe, crearla

Sin el Lock, esto podría pasar:
    Hilo A: revisa la URL "x.com" -> no existe
    Hilo B: revisa la URL "x.com" -> no existe (al mismo tiempo que A)
    Hilo A: la inserta
    Hilo B: también la inserta  --> ¡URL DUPLICADA! (esto es una "condición
                                     de carrera" o race condition)

Con el Lock, el hilo B tiene que ESPERAR a que A termine sus dos pasos
antes de poder siquiera empezar a revisar. Así nunca hay dos hilos
"a mitad de camino" del mismo chequeo al mismo tiempo.
"""

import queue
import threading
from app.models import Url

# Un único candado global, compartido por TODOS los hilos del pool.
# Si cada hilo tuviera su propio Lock, sería inútil: la gracia es que
# todos respeten el mismo candado.
lock_encolado = threading.Lock()


class ColaDeUrls:
    """Envuelve una queue.Queue para manejar ids de URLs pendientes."""

    def __init__(self):
        self._cola = queue.Queue()

    def encolar_url(self, session, busqueda_id, fuente_id, url, profundidad=0):
        """
        Registra una URL nueva en la base de datos (si no existe ya para
        esta búsqueda) y la agrega a la cola de trabajo en memoria.
        """
        with lock_encolado:  # <- aquí se "cierra" el candado
            existe = session.query(Url).filter_by(
                busqueda_id=busqueda_id, url=url
            ).first()
            if existe:
                return  # ya estaba registrada; RF6 exige evitar duplicados

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
        # <- aquí se "abre" el candado automáticamente al salir del `with`

    def obtener_url(self, timeout=2):
        """Saca un id de URL de la cola. Devuelve None si no hay nada (timeout)."""
        try:
            return self._cola.get(timeout=timeout)
        except queue.Empty:
            return None

    def esta_vacia(self):
        return self._cola.empty()