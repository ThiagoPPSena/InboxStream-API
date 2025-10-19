# alembic/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine # <-- NOVO
from sqlalchemy.engine import Connection              # <-- NOVO
from alembic import context

# Importações do Projeto FastAPI:
from app.database.base import Base                  # <-- NOVO: Base Declarativa
from app.database.config import settings            # <-- NOVO: Objeto de Configuração
from app.database import models                     # <-- NOVO: Garante que os modelos sejam importados

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata # <-- ALTERADO: Agora aponta para a Base do seu projeto

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# --- Funções Auxiliares ---
# Função auxiliar para ser executada sincronicamente dentro da conexão assíncrona
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()
# --------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Para o modo offline, você ainda precisa de uma URL síncrona no alembic.ini
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    Usa o motor assíncrono e o asyncio para executar a migração.
    """
    
    # 1. Cria o motor de conexão assíncrona usando a URL de DB do settings
    connectable = create_async_engine(
        # settings.DATABASE_URL é 'postgresql+asyncpg://...'
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    # 2. Define a função assíncrona que executa a migração
    async def run_async_migrations():
        async with connectable.connect() as connection:
            # Envia a função de migração síncrona para ser executada 
            # dentro do contexto assíncrono da conexão
            await connection.run_sync(do_run_migrations)

    # 3. Executa o loop assíncrono
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()