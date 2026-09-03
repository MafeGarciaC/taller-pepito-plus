"""
Rutas de la aplicación web.
"""

from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from app import SessionLocal
from app.models import Fuente, Persona, Busqueda, Documento, DocumentoAnalisis, MetricaConcurrencia
from app.crawler import ejecutar_crawling

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return jsonify({"status": "ok", "mensaje": "Pepito Plus API funcionando"})


@bp.route("/test-db")
def test_db():
    """Prueba que la conexión a MySQL funciona haciendo una consulta simple."""
    session = SessionLocal()
    try:
        count = session.query(Fuente).count()
        return jsonify({
            "status": "ok",
            "conexion": "exitosa",
            "fuentes_registradas": count
        })
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500
    finally:
        session.close()


# ============================================================
# RF1 - Registro de persona a consultar
# ============================================================

@bp.route("/personas/nueva", methods=["GET", "POST"])
def registrar_persona():
    if request.method == "GET":
        return render_template("registrar_persona.html")

    # POST: procesar el formulario
    nombre_completo = request.form.get("nombre_completo", "").strip()
    pais = request.form.get("pais", "").strip()
    ciudad = request.form.get("ciudad", "").strip()
    profesion_cargo = request.form.get("profesion_cargo", "").strip()
    empresa_organizacion = request.form.get("empresa_organizacion", "").strip()
    alias = request.form.get("alias", "").strip()
    palabras_relacionadas = request.form.get("palabras_relacionadas", "").strip()

    # Validación de campos obligatorios (RF1: nombre completo y país)
    if not nombre_completo or not pais:
        flash("El nombre completo y el país son obligatorios.", "error")
        return render_template("registrar_persona.html", form_data=request.form)

    session = SessionLocal()
    try:
        nueva_persona = Persona(
            nombre_completo=nombre_completo,
            pais=pais,
            ciudad=ciudad or None,
            profesion_cargo=profesion_cargo or None,
            empresa_organizacion=empresa_organizacion or None,
            alias=alias or None,
            palabras_relacionadas=palabras_relacionadas or None,
        )
        session.add(nueva_persona)
        session.commit()
        flash(f"Persona '{nombre_completo}' registrada correctamente.", "exito")
        return redirect(url_for("main.listado_personas"))
    except Exception as e:
        session.rollback()
        flash(f"Error al guardar: {str(e)}", "error")
        return render_template("registrar_persona.html", form_data=request.form)
    finally:
        session.close()


@bp.route("/personas")
def listado_personas():
    session = SessionLocal()
    try:
        personas = session.query(Persona).order_by(Persona.fecha_registro.desc()).all()
        return render_template("listado_personas.html", personas=personas)
    finally:
        session.close()


# ============================================================
# RF2 - Administración de fuentes por país
# ============================================================

TIPOS_VALIDOS = {"NOTICIAS", "RED_SOCIAL", "BLOG", "DIRECTORIO", "GUBERNAMENTAL", "OTRO"}
ESTADOS_VALIDOS = {"ACTIVA", "INACTIVA"}


@bp.route("/fuentes/nueva", methods=["GET", "POST"])
def registrar_fuente():
    if request.method == "GET":
        return render_template("registrar_fuente.html")

    nombre = request.form.get("nombre", "").strip()
    url_inicial = request.form.get("url_inicial", "").strip()
    pais = request.form.get("pais", "").strip()
    tipo = request.form.get("tipo", "").strip()
    estado = request.form.get("estado", "").strip()

    # Validación: los 5 campos son obligatorios según RF2
    if not all([nombre, url_inicial, pais, tipo, estado]):
        flash("Todos los campos son obligatorios.", "error")
        return render_template("registrar_fuente.html", form_data=request.form)

    if tipo not in TIPOS_VALIDOS or estado not in ESTADOS_VALIDOS:
        flash("Tipo o estado inválido.", "error")
        return render_template("registrar_fuente.html", form_data=request.form)

    session = SessionLocal()
    try:
        nueva_fuente = Fuente(
            nombre=nombre,
            url_inicial=url_inicial,
            pais=pais,
            tipo=tipo,
            estado=estado,
        )
        session.add(nueva_fuente)
        session.commit()
        flash(f"Fuente '{nombre}' registrada correctamente.", "exito")
        return redirect(url_for("main.listado_fuentes"))
    except Exception as e:
        session.rollback()
        flash(f"Error al guardar: {str(e)}", "error")
        return render_template("registrar_fuente.html", form_data=request.form)
    finally:
        session.close()


@bp.route("/fuentes")
def listado_fuentes():
    session = SessionLocal()
    try:
        fuentes = session.query(Fuente).order_by(Fuente.fecha_registro.desc()).all()
        return render_template("listado_fuentes.html", fuentes=fuentes)
    finally:
        session.close()


@bp.route("/fuentes/<int:fuente_id>/toggle", methods=["POST"])
def toggle_fuente(fuente_id):
    """Activa o desactiva una fuente (RF2: estado activa/inactiva)."""
    session = SessionLocal()
    try:
        fuente = session.query(Fuente).get(fuente_id)
        if not fuente:
            flash("Fuente no encontrada.", "error")
            return redirect(url_for("main.listado_fuentes"))

        fuente.estado = "INACTIVA" if fuente.estado == "ACTIVA" else "ACTIVA"
        session.commit()
        flash(f"Fuente '{fuente.nombre}' ahora está {fuente.estado}.", "exito")
        return redirect(url_for("main.listado_fuentes"))
    except Exception as e:
        session.rollback()
        flash(f"Error al actualizar: {str(e)}", "error")
        return redirect(url_for("main.listado_fuentes"))
    finally:
        session.close()


# ============================================================
# RF3 - Crawling concurrente (inicio de búsqueda)
# ============================================================

@bp.route("/busquedas/nueva", methods=["GET", "POST"])
def nueva_busqueda():
    session = SessionLocal()
    try:
        if request.method == "GET":
            personas = session.query(Persona).all()
            return render_template("nueva_busqueda.html", personas=personas)

        persona_id = int(request.form.get("persona_id"))
        pais = request.form.get("pais", "").strip()
        num_workers = int(request.form.get("num_workers", 5))

        if not pais:
            flash("El país es obligatorio.", "error")
            personas = session.query(Persona).all()
            return render_template("nueva_busqueda.html", personas=personas)

        nueva = Busqueda(persona_id=persona_id, pais=pais, num_workers=num_workers)
        session.add(nueva)
        session.commit()
        busqueda_id = nueva.id
    finally:
        session.close()

    # El crawling corre aquí de forma sincrona: la petición HTTP espera
    # hasta que termine. Para el taller esto es suficiente; en producción
    # se lanzaría en segundo plano (ej. con Celery) para no bloquear al usuario.
    resultado = ejecutar_crawling(busqueda_id, persona_id, pais, num_workers=num_workers)

    flash(
        f"Crawling completado: {resultado['procesadas']} URLs procesadas "
        f"en {resultado['tiempo_ms']} ms con {num_workers} workers.",
        "exito"
    )
    return redirect(url_for("main.detalle_busqueda", busqueda_id=busqueda_id))


@bp.route("/busquedas/<int:busqueda_id>")
def detalle_busqueda(busqueda_id):
    session = SessionLocal()
    try:
        busqueda = session.query(Busqueda).get(busqueda_id)
        documentos = session.query(Documento).filter_by(busqueda_id=busqueda_id).all()
        return render_template("detalle_busqueda.html", busqueda=busqueda, documentos=documentos)
    finally:
        session.close()


# ============================================================
# RF9 - Consulta y filtrado de resultados
# ============================================================

@bp.route("/resultados")
def resultados():
    session = SessionLocal()
    try:
        query = (
            session.query(Documento)
            .join(Fuente, Documento.fuente_id == Fuente.id)
            .outerjoin(DocumentoAnalisis, Documento.id == DocumentoAnalisis.documento_id)
        )

        clasificacion = request.args.get("clasificacion", "").strip()
        verificacion = request.args.get("verificacion", "").strip()
        fuente_id = request.args.get("fuente_id", "").strip()
        fecha_desde = request.args.get("fecha_desde", "").strip()
        fecha_hasta = request.args.get("fecha_hasta", "").strip()

        if clasificacion:
            query = query.filter(DocumentoAnalisis.clasificacion_contextual == clasificacion)

        if verificacion:
            if verificacion == "SIN_ANALIZAR":
                query = query.filter(DocumentoAnalisis.id.is_(None))
            else:
                query = query.filter(DocumentoAnalisis.verificacion_identidad == verificacion)

        if fuente_id:
            query = query.filter(Documento.fuente_id == int(fuente_id))

        if fecha_desde:
            query = query.filter(Documento.fecha_consulta >= fecha_desde)

        if fecha_hasta:
            query = query.filter(Documento.fecha_consulta <= f"{fecha_hasta} 23:59:59")

        documentos = query.order_by(Documento.fecha_consulta.desc()).all()
        fuentes = session.query(Fuente).all()

        return render_template(
            "resultados.html",
            documentos=documentos,
            fuentes=fuentes,
            filtros=request.args,
        )
    finally:
        session.close()


# ============================================================
# Medición de concurrencia (nota de la rúbrica)
# ============================================================

@bp.route("/metricas")
def metricas():
    session = SessionLocal()
    try:
        registros = (
            session.query(MetricaConcurrencia)
            .order_by(MetricaConcurrencia.fecha_ejecucion.asc())
            .all()
        )
        max_tiempo = max([m.tiempo_total_ms for m in registros], default=1)
        return render_template("metricas.html", metricas=registros, max_tiempo=max_tiempo)
    finally:
        session.close()