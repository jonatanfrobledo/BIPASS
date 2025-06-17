from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (en la raíz del proyecto)
load_dotenv()

# Agregar el path del proyecto para que Alembic encuentre tus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar modelos para que estén registrados en metadata
# Importa aquí todos tus modelos para que Alembic los reconozca en la metadata
from app.models.user import User
from app.models.event import Event
from app.models.venue import Venue
from app.models.ticket import Ticket
from app.models.order import Order
from app.models.payment import Payment
from app.models.review import Review

# Importar engine de base de datos
from app.db.session import engine

# Alembic Config
config = context.config

# Interpretar el archivo .ini con fileConfig (para logs)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Configurar la URL de la base de datos
database_url = os.getenv("DATABASE_URL")
if database_url:
    # Reemplazo de protocolo para compatibilidad PostgreSQL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", database_url)

# Metadata que Alembic va a usar para autogenerar migraciones
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Ejecutar migraciones en modo offline sin conexión directa."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecutar migraciones en modo online con conexión a DB."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Opcional: detecta cambios en tipos de columnas
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
