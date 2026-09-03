from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
 
from config import Config
from app.models import Base
 
 
# Motor de conexión a MySQL, compartido por toda la app
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False, pool_pre_ping=True)
 
# Fábrica de sesiones (cada request/hilo puede pedir su propia sesión)
SessionLocal = scoped_session(sessionmaker(bind=engine))
 
 
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
 
    # Crea automáticamente las tablas si no existen todavía
    # (no es obligatorio si ya corriste schema.sql, pero es una red de seguridad)
    Base.metadata.create_all(bind=engine)
 
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
 
    return app
 