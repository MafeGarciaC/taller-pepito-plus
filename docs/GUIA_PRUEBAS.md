# Guía de flujo y pruebas — Pepito Plus

> Taller Práctico #1 · Sistemas Distribuidos · CECAR  
> Aplicación: Flask + MySQL · Puerto: `localhost:5000`

---

## 1. Preparación del entorno

```bash
# Recrear el entorno virtual (solo si es la primera vez o cambió de equipo)
python -m venv venv

# Activar (Windows PowerShell)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser   # solo la primera vez
.\venv\Scripts\Activate.ps1

# Activar (Windows cmd)
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales — editar .env
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pepito_plus

# Crear la base de datos en MySQL (solo una vez)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS pepito_plus CHARACTER SET utf8mb4;"

# Levantar la aplicación
python run.py
```

Abrir `http://localhost:5000` → debe mostrar el **panel de inicio** con los 7 accesos directos.

---

## 2. Flujo completo paso a paso

### Paso 1 — Registrar una persona (RF1)
**Ruta:** `/personas/nueva`

| Campo | Obligatorio | Ejemplo |
|-------|-------------|---------|
| Nombre completo | ✅ | Gustavo Petro |
| País | ✅ | Colombia |
| Ciudad | | Bogotá |
| Profesión/cargo | | Presidente |
| Empresa/organización | | Presidencia de Colombia |
| Alias | | Petro |
| Palabras relacionadas | | gobierno, reforma, paz total |

**Prueba:** enviar el formulario → debe redirigir a `/personas` y mostrar la persona en la tabla.  
**Prueba negativa:** enviar sin nombre → debe mostrar error de validación, no crear registro.

---

### Paso 2 — Registrar fuentes (RF2)
**Ruta:** `/fuentes/nueva`

Registrar al menos 2 fuentes activas para Colombia:

| Nombre | URL inicial | País | Tipo | Estado |
|--------|-------------|------|------|--------|
| El Tiempo | https://www.eltiempo.com | Colombia | NOTICIAS | ACTIVA |
| El Espectador | https://www.elespectador.com | Colombia | NOTICIAS | ACTIVA |
| Semana | https://www.semana.com | Colombia | NOTICIAS | ACTIVA |

**Prueba:** ir a `/fuentes` → ver las fuentes con badge verde ACTIVA.  
**Prueba toggle:** hacer clic en "Desactivar" → badge cambia a INACTIVA; volver a "Activar" → ACTIVA de nuevo.

---

### Paso 3 — Ejecutar búsqueda con crawler (RF3, RF4, RF5, RF6, RF7, RF8)
**Ruta:** `/busquedas/nueva`

1. Seleccionar la persona registrada en el Paso 1.
2. Escribir el país: `Colombia`.
3. Configurar workers: **5** (primera corrida).
4. Clic en **Iniciar crawling** — la página queda cargando mientras corren los threads.
5. Al terminar redirige automáticamente a `/busquedas/<id>` con el detalle.

**Qué verificar en el detalle:**
- Tabla "Documentos relacionados": documentos con `es_relacionado = True`, con verificación de identidad y clasificación contextual.
- Tabla "Documentos descartados": documentos con motivo de descarte (ej: `"No menciona: Gustavo Petro"`).
- El contador de workers usados aparece en el encabezado.

---

### Paso 4 — Consultar y filtrar resultados (RF9)
**Ruta:** `/resultados`

Columnas visibles: Título · URL · Fuente · País · Fecha publicación · Fecha consulta · Verificación · Clasificación · Fragmento.

**Pruebas de filtros:**

| Filtro | Valor de prueba | Resultado esperado |
|--------|-----------------|--------------------|
| Clasificación | POSITIVO | Solo docs con contexto positivo |
| Clasificación | NEGATIVO | Solo docs con contexto negativo |
| Verificación | MISMA_PERSONA | Solo coincidencias fuertes |
| Verificación | POSIBLE_COINCIDENCIA | Coincidencias débiles |
| Verificación | PERSONA_DIFERENTE | Docs de otra persona |
| Fuente | El Tiempo | Solo docs de esa fuente |
| Fecha desde | 2024-01-01 | Docs desde esa fecha |
| Filtros combinados | MISMA_PERSONA + NEGATIVO | Docs negativos de la persona |
| Filtros imposibles | PERSONA_DIFERENTE + NEGATIVO | 0 resultados (RF8 solo aplica a MISMA/POSIBLE) |

---

### Paso 5 — Medir concurrencia (Nota rúbrica 3%)
**Ruta:** `/metricas`

Ejecutar **dos búsquedas con la misma persona y país**, variando solo los workers:

| Corrida | Persona | País | Workers | Tiempo esperado |
|---------|---------|------|---------|-----------------|
| 1 | Gustavo Petro | Colombia | 1 | ~200 s |
| 2 | Gustavo Petro | Colombia | 5 | ~80 s |

En `/metricas` aparece la comparación visual con barras proporcionales.  
**Análisis a mencionar en sustentación:** la mejora ~2.4x con 5 workers se explica porque el crawler es I/O-bound (espera respuestas HTTP); la ganancia no es lineal por la contención en `lock_encolado` y `lock_reclamo`.

---

## 3. Checklist de rúbrica

| RF | Criterio | Dónde verificar |
|----|----------|-----------------|
| RF1 | Registro con todos los campos, validación de obligatorios, persistencia | `/personas/nueva` → `/personas` |
| RF2 | Nombre, URL, país, tipo, estado; toggle activa/inactiva | `/fuentes/nueva` → `/fuentes` |
| RF3 | Pool configurable, múltiples workers, cola compartida, crawling paralelo | **Logs en terminal** — ver sección 4.1 |
| RF4 | Estados PENDIENTE→EN_PROCESAMIENTO→PROCESADA/DESCARTADA/ERROR; sin duplicados | **MySQL durante crawling** — ver sección 4.2 |
| RF5 | Coincidencia por nombre/alias/ciudad/profesión/empresa/palabras; motivo de descarte | `/busquedas/<id>` tabla descartados |
| RF6 | Título, URL, fuente, país, fecha publicación, fecha consulta, contenido; sin duplicados | `/busquedas/<id>` tabla relacionados |
| RF7 | MISMA_PERSONA / POSIBLE_COINCIDENCIA / PERSONA_DIFERENTE / NO_DETERMINADO | `/busquedas/<id>` columna Verificación |
| RF8 | POSITIVO / NEUTRO / NEGATIVO / NO_DETERMINADO solo en MISMA/POSIBLE | `/resultados` columna Clasificación |
| RF9 | Todas las columnas requeridas + 5 filtros funcionales | `/resultados` |
| Concurrencia | Comparación 1 vs N workers con métricas reales | `/metricas` — ver sección 4.3 |

---

## 4. Cómo demostrar concurrencia real (RF3 y RF4)

### 4.1 Evidencia en la terminal (la más directa)

Al iniciar una búsqueda con `num_workers=5`, la terminal muestra esto en tiempo real:

```
============================================================
  CRAWLING INICIADO | workers=5 | fuentes=3
============================================================
[20:41:03.112] [ThreadPoolExecutor-0_0] → https://www.eltiempo.com
[20:41:03.118] [ThreadPoolExecutor-0_1] → https://www.elespectador.com
[20:41:03.124] [ThreadPoolExecutor-0_2] → https://www.semana.com
[20:41:04.203] [ThreadPoolExecutor-0_0] ✓ PROCESADA
[20:41:04.891] [ThreadPoolExecutor-0_3] → https://www.eltiempo.com/politica/...
[20:41:04.902] [ThreadPoolExecutor-0_1] ✓ DESCARTADA
[20:41:04.910] [ThreadPoolExecutor-0_4] → https://www.elespectador.com/noticias/...
============================================================
  CRAWLING COMPLETADO | URLs=50 | Tiempo=38420 ms (38.4 s)
============================================================
```

**Lo que prueba:** los timestamps `03.112`, `03.118`, `03.124` son **distintos hilos iniciando casi simultáneamente**. Si fuera secuencial, cada URL esperaría a que la anterior terminara (~8 s de timeout HTTP). Los nombres `ThreadPoolExecutor-0_0` a `ThreadPoolExecutor-0_4` son los 5 threads del pool creados por `ThreadPoolExecutor(max_workers=5)`.

---

### 4.2 Evidencia en MySQL durante el crawling (RF4)

Mientras corre la búsqueda (ventana de ~30 s), ejecutar en Workbench:

```sql
-- Muestra URLs siendo procesadas en paralelo en este instante
SELECT estado, worker_id, url
FROM pepito_plus.urls
WHERE estado = 'EN_PROCESAMIENTO'
ORDER BY id DESC
LIMIT 20;
```

Con `num_workers=5` aparecen **varias filas** con `EN_PROCESAMIENTO` simultáneamente.  
Con `num_workers=1` aparece **solo una** a la vez.  
Eso es la prueba en base de datos del lock atómico del RF4: cada worker reclama su URL con `lock_reclamo` antes de cambiar el estado.

```sql
-- Resumen de estados al finalizar
SELECT estado, COUNT(*) AS total
FROM pepito_plus.urls
GROUP BY estado;
```

Resultado esperado:

| estado | total |
|--------|-------|
| PROCESADA | ~42 |
| DESCARTADA | ~6 |
| ERROR | ~2 |
| PENDIENTE | 0 |

Que no quede ninguna en PENDIENTE confirma que todos los workers terminaron correctamente.

---

### 4.3 Evidencia en /metricas (la más visual para sustentación)

| Corrida | Workers | Tiempo total | ms/URL |
|---------|---------|-------------|--------|
| #1 | 1 | ~190 s | ~3 800 ms |
| #2 | 5 | ~42 s | ~840 ms |

La mejora ~4.5× con 5 workers (siendo el crawler I/O-bound) demuestra ejecución paralela real. No es lineal porque el `lock_encolado` introduce contención cuando varios threads intentan encolar nuevas URLs al mismo tiempo.

---

## 5. Comandos útiles de verificación en MySQL

```sql
-- Ver URLs por estado
SELECT estado, COUNT(*) FROM pepito_plus.urls GROUP BY estado;

-- Ver documentos con su análisis
SELECT d.titulo, d.url, da.verificacion_identidad, da.clasificacion_contextual
FROM pepito_plus.documentos d
LEFT JOIN pepito_plus.documento_analisis da ON d.id = da.documento_id
LIMIT 20;

-- Ver documentos descartados con motivo
SELECT titulo, motivo_descarte
FROM pepito_plus.documentos
WHERE es_relacionado = 0
LIMIT 20;

-- Ver métricas de concurrencia
SELECT busqueda_id, num_workers, tiempo_total_ms, elementos_procesados
FROM pepito_plus.metricas_concurrencia;
```

> **Nota:** siempre usar el prefijo `pepito_plus.` en Workbench o ejecutar `USE pepito_plus;` al inicio de la sesión.

---

## 6. Errores comunes y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `Access Denied (1045)` | Credenciales incorrectas en `.env` | Corregir `DB_PASSWORD` |
| `.\venv\Scripts\Activate.ps1` no reconocido | Política de ejecución de PowerShell | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `Table 'pepito_plus.X' doesn't exist` | BD no inicializada | Levantar app una vez con `python run.py` (SQLAlchemy crea las tablas) |
| `Error Code: 1046. No database selected` | Workbench sin esquema activo | Agregar prefijo `pepito_plus.` a las tablas o ejecutar `USE pepito_plus;` |
| Crawler termina sin documentos | No hay fuentes activas para el país | Registrar fuentes con estado ACTIVA y el mismo país de la búsqueda |
| Clasificación = N/A en todos los docs | RF7 no encontró MISMA/POSIBLE | Usar una persona conocida públicamente con contenido real en Internet |
