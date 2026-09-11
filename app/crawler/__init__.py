import time
from concurrent.futures import ThreadPoolExecutor

from app import SessionLocal
from app.models import Busqueda, Fuente, MetricaConcurrencia
from app.crawler.queue_manager import ColaDeUrls
from app.crawler.worker import procesar_url


def ejecutar_crawling(busqueda_id, persona_id, pais, num_workers=5, max_urls=50):
    session = SessionLocal()
    cola = ColaDeUrls()
    inicio = time.time()

    try:
        fuentes_activas = session.query(Fuente).filter_by(pais=pais, estado="ACTIVA").all()
        for fuente in fuentes_activas:
            cola.encolar_url(session, busqueda_id, fuente.id, fuente.url_inicial, profundidad=0)

        procesadas = 0
        worker_counter = 0

        # Pool de hilos reutilizables; num_workers es configurable (RF3)
        print(f"\n{'='*60}")
        print(f"  CRAWLING INICIADO | workers={num_workers} | fuentes={len(fuentes_activas)}")
        print(f"{'='*60}")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futuros = []

            while procesadas < max_urls:
                url_id = cola.obtener_url(timeout=3)

                if url_id is None:
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

            for f in futuros:
                f.result()

        tiempo_total_ms = int((time.time() - inicio) * 1000)
        print(f"{'='*60}")
        print(f"  CRAWLING COMPLETADO | URLs={procesadas} | Tiempo={tiempo_total_ms} ms ({tiempo_total_ms/1000:.1f} s)")
        print(f"{'='*60}\n")

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
