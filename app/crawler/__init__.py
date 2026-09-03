"""
Orquestador del crawler concurrente (RF3).

--------------------------------------------------------------------
CONCEPTO 4: ThreadPoolExecutor
--------------------------------------------------------------------
En vez de crear un hilo nuevo por cada URL (crear hilos tiene costo, y con
miles de URLs sería un desperdicio), un "pool" (grupo) crea de una vez
N hilos reutilizables. Le entregas tareas con `executor.submit(funcion,
argumentos)` y el pool decide, según qué hilos están libres, cuál las
ejecuta. Esto es exactamente lo que pide RF3: "un pool de múltiples
threads/workers... el número máximo de workers deberá ser configurable".

--------------------------------------------------------------------
CONCEPTO 5: ¿por qué threads y no procesos (multiprocessing)?
--------------------------------------------------------------------
Python tiene el GIL (Global Interpreter Lock): un candado interno que
impide que dos threads ejecuten bytecode Python al mismo tiempo dentro
de un mismo proceso. Esto suena como que "los threads no sirven para
nada en Python", pero hay una excepción clave: el GIL SE LIBERA mientras
un thread está esperando una operación de Entrada/Salida (I/O) -- como
esperar la respuesta de una petición HTTP con requests.get().

Este crawler es "I/O-bound": la mayor parte del tiempo NO se gasta
calculando, se gasta esperando que el servidor remoto responda. Mientras
el Hilo A espera la respuesta de eltiempo.com, el GIL queda libre y el
Hilo B puede aprovechar para hacer su propia petición. Por eso threads
funcionan muy bien aquí, y son más livianos que procesos separados
(multiprocessing), que sí tendría más sentido si el cuello de botella
fuera cómputo puro en CPU (por ejemplo, procesar imágenes o video).
"""

import time
from concurrent.futures import ThreadPoolExecutor

from app import SessionLocal
from app.models import Busqueda, Fuente, MetricaConcurrencia
from app.crawler.queue_manager import ColaDeUrls
from app.crawler.worker import procesar_url


def ejecutar_crawling(busqueda_id, persona_id, pais, num_workers=5, max_urls=50):
    """
    Punto de entrada del crawler:
    1. Siembra la cola con las Seed URLs de las fuentes activas del país (RF2, RF3)
    2. Lanza el pool de workers para procesar la cola hasta que se vacíe
       o se alcance el límite de exploración (max_urls)
    3. Registra métricas de tiempo (para comparar 1 vs N workers)
    """
    session = SessionLocal()
    cola = ColaDeUrls()
    inicio = time.time()

    try:
        fuentes_activas = session.query(Fuente).filter_by(pais=pais, estado="ACTIVA").all()
        for fuente in fuentes_activas:
            cola.encolar_url(session, busqueda_id, fuente.id, fuente.url_inicial, profundidad=0)

        procesadas = 0
        worker_counter = 0

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futuros = []

            while procesadas < max_urls:
                url_id = cola.obtener_url(timeout=3)

                if url_id is None:
                    # No hay URLs esperando en este instante. Si además ya
                    # no quedan tareas en vuelo, terminamos: no va a
                    # aparecer nada nuevo.
                    if all(f.done() for f in futuros) and cola.esta_vacia():
                        break
                    continue

                worker_counter += 1
                worker_id = f"worker-{worker_counter % num_workers}"

                futuro = executor.submit(
                    procesar_url, url_id, busqueda_id, persona_id, cola, worker_id
                )
                futuros.append(futuro)
                procesadas += 1

            # Espera a que terminen todas las tareas enviadas al pool
            for f in futuros:
                f.result()

        tiempo_total_ms = int((time.time() - inicio) * 1000)

        metrica = MetricaConcurrencia(
            busqueda_id=busqueda_id,
            fase="CRAWLING",
            num_workers=num_workers,
            tiempo_total_ms=tiempo_total_ms,
            elementos_procesados=procesadas,
        )
        session.add(metrica)

        busqueda = session.query(Busqueda).get(busqueda_id)
        busqueda.estado = "COMPLETADA"
        busqueda.num_workers = num_workers
        session.commit()

        return {"procesadas": procesadas, "tiempo_ms": tiempo_total_ms}

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()