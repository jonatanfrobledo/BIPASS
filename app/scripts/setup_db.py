import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Cargar variables de entorno
load_dotenv()

def create_database():
    """Crea la base de datos si no existe."""
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Verificar si la base de datos existe
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bipass_db'")
        exists = cur.fetchone()
        
        if not exists:
            # Crear la base de datos
            cur.execute('CREATE DATABASE bipass_db')
            print("Base de datos 'bipass_db' creada exitosamente.")
        else:
            print("La base de datos 'bipass_db' ya existe.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
        sys.exit(1)

def run_migrations():
    """Ejecuta las migraciones de Alembic."""
    try:
        from alembic.config import Config
        from alembic import command
        
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Ejecutar migraciones
        command.upgrade(alembic_cfg, "head")
        print("Migraciones ejecutadas exitosamente.")
        
    except Exception as e:
        print(f"Error al ejecutar las migraciones: {e}")
        sys.exit(1)

def create_initial_data():
    """Crea datos iniciales necesarios."""
    try:
        from app.db.session import SessionLocal
        from app.models.user import User, UserRole
        from app.utils.auth import get_password_hash
        
        db = SessionLocal()
        
        # Verificar si ya existe un usuario admin
        admin = db.query(User).filter(User.email == "admin@bipass.com").first()
        if not admin:
            # Crear usuario administrador
            admin_user = User(
                name="Administrator",
                email="admin@bipass.com",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Usuario administrador creado exitosamente.")
        else:
            print("El usuario administrador ya existe.")
        
        db.close()
        
    except Exception as e:
        print(f"Error al crear datos iniciales: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Iniciando configuración de la base de datos...")
    create_database()
    run_migrations()
    create_initial_data()
    print("Configuración completada exitosamente.")