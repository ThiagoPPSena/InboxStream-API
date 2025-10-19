# app/database/base.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.database.config import settings

# 1. Cria o motor de banco de dados assíncrono
# echo=True é útil para depuração, mostrando as queries SQL geradas
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# 2. Cria a sessão assíncrona (a ser usada nas dependências do FastAPI)
# expire_on_commit=False é uma boa prática com sessões assíncronas
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 3. Base declarativa para os modelos ORM (o coração do Alembic)
Base = declarative_base()

# 4. Função de dependência para injetar a sessão na rota do FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session