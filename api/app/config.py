from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres lus dans les variables d'environnement (ou un fichier .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://rf:rf@localhost:5432/rf"
    secret_key: str = "dev-only-change-me"
    session_hours: int = 10
    cookie_secure: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]


settings = Settings()
