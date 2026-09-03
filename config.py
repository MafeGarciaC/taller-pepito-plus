import os
from dotenv import load_dotenv
 
# Carga las variables definidas en .env al entorno del proceso
load_dotenv()
 
 
class Config:
    # Necesaria para que funcionen los mensajes flash (éxito/error) en los formularios
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-desarrollo-cambiar-en-produccion")
 
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
 
    # Cadena de conexión para SQLAlchemy usando el driver pymysql
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
 
    # Evita overhead innecesario de SQLAlchemy (recomendado con Flask)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    # Configuración del crawler (RF3) - número máximo de workers, configurable
    CRAWLER_MAX_WORKERS = int(os.getenv("CRAWLER_MAX_WORKERS", 5))
    CRAWLER_MAX_URLS = int(os.getenv("CRAWLER_MAX_URLS", 100))