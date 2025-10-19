# app/database/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

# Classe para carregar variáveis de ambiente (DB_USER, DB_PASS, etc.)
class Settings(BaseSettings):
    # Valores do seu novo contêiner na porta 5434
    DB_HOST: str = "localhost"
    DB_PORT: int = 5434
    DB_USER: str = "inbox_user"
    DB_PASS: str = "inbox_pass"
    DB_NAME: str = "inboxstream_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """String de conexão assíncrona para o asyncpg."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    # Define o arquivo .env como fonte de configuração
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()