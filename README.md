# Pepito Plus

Sistema de búsqueda concurrente de información pública sobre una persona en Internet, con crawling multihilo, verificación de identidad y clasificación contextual del contenido encontrado.

**Taller Práctico #1**

---

## Tecnologías utilizadas

- **Backend:** Python 3.12 + Flask
- **Base de datos:** MySQL + SQLAlchemy (ORM)
- **Concurrencia:** `threading` (Lock) + `concurrent.futures.ThreadPoolExecutor`
- **Crawling:** `requests` + `BeautifulSoup4`

---

## Instalación paso a paso

### 1. Clona el repositorio

```bash
git clone https://github.com/MafeGarciaC/taller-pepito-plus.git
cd taller-pepito-plus
```

### 2. Crea y activa el entorno virtual

```powershell
python -m venv venv
venv\Scripts\activate      
```

### 3. Instala las dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configura las variables de entorno

Copia el archivo de ejemplo y complétalo con tus propios datos:

Abre `.env` y ajusta al menos `DB_PASSWORD` con la contraseña real de tu usuario `root` de MySQL.

### 5. Crea la base de datos

Abre **MySQL Workbench**, conéctate a tu servidor local, y ejecuta el script de esquema:

```
 cd Database/pepito_plus.sql > Ejecutar 
```


### 6. Corre la aplicación

```
python run.py
```

Abre el navegador en: **http://localhost:5000**

---

## Cómo usar el sistema

| Ruta | Qué hace |
|---|---|
| `/personas/nueva` | Registrar una persona a consultar (RF1) |
| `/personas` | Ver personas registradas |
| `/fuentes/nueva` | Registrar una fuente pública (RF2) |
| `/fuentes` | Ver fuentes y activar/desactivar |
| `/busquedas/nueva` | Iniciar el crawler concurrente (RF3) |
| `/busquedas/<id>` | Ver resultados de una búsqueda (RF5, RF6, RF7, RF8) |
| `/resultados` | Consultar y filtrar todos los documentos encontrados (RF9) |
| `/metricas` | Comparar tiempos de ejecución por número de workers |

**Nota:** al lanzar una búsqueda, la página tarda entre 30 segundos y varios minutos en responder — es normal, el crawler está trabajando en segundo plano dentro de esa misma petición.

---

## Estructura del proyecto

```
taller-pepito-plus/
├── app/
│   ├── routes.py          # Rutas web (Flask)
│   ├── models.py          # Modelos de base de datos (SQLAlchemy)
│   ├── crawler/
│   │   ├── __init__.py    # Orquestador (ThreadPoolExecutor) - RF3
│   │   ├── queue_manager.py  # Cola compartida (Queue + Lock) - RF3, RF4
│   │   └── worker.py      # Lógica de cada worker - RF4-RF8
│   ├── services/
│   │   ├── matching.py    # RF5 - contenido relacionado
│   │   ├── identity.py    # RF7 - verificación de identidad
│   │   └── classifier.py  # RF8 - clasificación contextual
│   └── templates/         # Vistas HTML (Jinja2)
├── database/
│   ├── pepito_plus.sql          # Creación de tablas
├── docs/
│   ├── bitacora_evidencias.md   # Evidencias paso a paso de cada RF
│   └── capturas/                # imagenes de evidencia
├── config.py
├── run.py
└── requirements.txt
```

