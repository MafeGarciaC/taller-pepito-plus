# Bitácora de Evidencias — Taller Práctico #1 (Pepito Plus)

> Instrucciones de uso: por cada avance, agrega una entrada nueva con el
> formato de abajo. No borres entradas viejas — esto se convierte en tu
> anexo de evidencias para el documento final y para la sustentación.

**Formato de cada entrada:**
```
### [Fecha] — [Nombre corto del avance]
**Sustenta:** RF#, o Entregable (Modelo de datos / Arquitectura / Infraestructura)
**Captura:** [nombre_archivo.png o "ver figura X"]
**Dónde se tomó:** [URL / herramienta / comando exacto]
**Qué demuestra:** [1-2 frases]
```

---

## 1. Configuración del entorno de desarrollo

### Estructura del proyecto y entorno virtual
**Sustenta:** Base para todos los RF (no es un requisito puntual, pero es prerrequisito)
**Captura:** `01_estructura_carpetas.png`
**Dónde se tomó:** VS Code, panel Explorer
**Qué demuestra:** Separación de responsabilidades por capas: rutas web, modelos de datos, lógica de crawling, y servicios de análisis (matching, identidad, clasificación) están en módulos independientes.

![Estructura de carpetas](capturas/01_estructura_carpetas.png)

---

**Captura:** `02_requirements_venv.png`
**Dónde se tomó:** Explorador de Windows, carpeta `taller-pepito-plus`
**Qué demuestra:** El entorno Python está aislado con sus dependencias (`flask`, `sqlalchemy`, `pymysql`, `requests`, `beautifulsoup4`) registradas en `requirements.txt`, permitiendo reproducibilidad.

![Entorno virtual y requirements](capturas/02_requirements_venv.png)

### Repositorio en GitHub
**Sustenta:** Requisito de entrega ("Entrega: Github")
**Captura:** `03_repo_github.png`
**Dónde se tomó:** GitHub, vista de repositorio `github.com/MafeGarciaC/taller-pepito-plus`
**Qué demuestra:** El código fuente está versionado y accesible; el `.gitignore` excluye correctamente `venv/` y `.env` para no exponer credenciales ni inflar el repositorio.

![Repositorio en GitHub](capturas/03_repo_github.png)

---

## 2. Modelo de datos (Entregable)

### Script de creación del esquema
**Sustenta:** Entregable "Modelo de datos"
**Captura:** (incluida en `schema.sql`, ver anexo de código)
**Dónde se tomó:** MySQL Workbench, `File > Open SQL Script`
**Qué demuestra:** Las 7 tablas (personas, fuentes, busquedas, urls, documentos, documento_analisis, metricas_concurrencia) y sus relaciones están formalmente definidas en SQL, con las restricciones de integridad (FK, UNIQUE, ENUM) que exige cada RF.

### Diagrama Entidad-Relación
**Sustenta:** Entregable "Modelo de datos"
**Captura:** `04_diagrama_er.png`
**Dónde se tomó:** MySQL Workbench, `Database > Reverse Engineer`
**Qué demuestra:** Las relaciones 1—N y 1—1 entre tablas reflejan el flujo de datos del sistema: una persona tiene múltiples búsquedas, cada búsqueda descubre URLs, cada URL puede generar un documento, y cada documento relacionado tiene un análisis de identidad/clasificación.

![Diagrama Entidad-Relación](capturas/04_diagrama_er.png)

### Confirmación de la base de datos creada
**Sustenta:** Entregable "Modelo de datos"
**Captura:** `05_show_databases.png`
**Dónde se tomó:** MySQL Workbench, pestaña de query — comando `SHOW DATABASES;`
**Qué demuestra:** El esquema fue aplicado exitosamente sobre una instancia real de MySQL, no solo definido en papel.

![SHOW DATABASES](capturas/05_show_databases.png)

---

## 3. Conexión de la aplicación a la base de datos

### Modelos SQLAlchemy
**Sustenta:** Prerrequisito técnico para RF1, RF2, RF6, RF7, RF8, RF9
**Captura:** `06_models_py.png`
**Dónde se tomó:** VS Code, archivo `app/models.py`
**Qué demuestra:** Cada tabla del modelo de datos tiene su representación en código Python (ORM), lo que permitirá insertar/consultar datos desde Flask sin escribir SQL manual.

![Modelos SQLAlchemy](capturas/06_models_py.png)

### Prueba de conexión extremo a extremo
**Sustenta:** Prerrequisito técnico transversal
**Captura:** `07_test_db_conexion.png`
**Dónde se tomó:** Navegador, `http://localhost:5000/test-db`
**Qué demuestra:** La cadena completa Flask → SQLAlchemy → MySQL funciona correctamente: la app puede levantar un servidor, conectarse a `pepito_plus`, y ejecutar una consulta real.

![Prueba de conexión](capturas/07_test_db_conexion.png)

---

## 4. Pendientes (se llenan a medida que avancemos)

### RF1 — Registro de persona
**Sustenta:** RF1
**Captura:** _(pendiente)_
**Dónde se tomó:** _(pendiente)_
**Qué demuestra:** _(pendiente)_

### RF2 — Administración de fuentes
**Sustenta:** RF2
**Captura:** _(pendiente)_

### RF3 — Crawling concurrente
**Sustenta:** RF3
**Captura:** _(pendiente — deberá incluir evidencia de múltiples workers ejecutando simultáneamente, ej. logs con timestamps o consola mostrando varios hilos activos)_

### RF4 — Control concurrente de URLs
**Sustenta:** RF4
**Captura:** _(pendiente — tabla `urls` en MySQL mostrando distintos estados)_

### RF5 — Identificación de contenido relacionado
**Sustenta:** RF5
**Captura:** _(pendiente — vista de documentos descartados con su motivo)_

### RF6 — Extracción, indexación y persistencia
**Sustenta:** RF6
**Captura:** _(pendiente — tabla `documentos` con registros reales)_

### RF7 — Verificación de identidad
**Sustenta:** RF7
**Captura:** _(pendiente — tabla `documento_analisis` con los 4 estados representados)_

### RF8 — Clasificación contextual
**Sustenta:** RF8
**Captura:** _(pendiente)_

### RF9 — Consulta y filtrado de resultados
**Sustenta:** RF9
**Captura:** _(pendiente — interfaz web con filtros aplicados)_

### Medición de concurrencia
**Sustenta:** Nota de medición de concurrencia (rúbrica)
**Captura:** _(pendiente — gráfica o tabla comparando tiempo con 1 worker vs. N workers)_

### Diagrama de arquitectura de software
**Sustenta:** Entregable
**Captura:** _(pendiente)_

### Diagrama de infraestructura
**Sustenta:** Entregable
**Captura:** _(pendiente)_
