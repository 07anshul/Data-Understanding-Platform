from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_user: str | None = None
    database_password: str | None = None
    database_name: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_url: str | None = None

    secret_key: str
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    upload_folder: str = "uploads"
    output_folder: str = "outputs"

    @property
    def sql_url(self):
        if self.database_url:
            return self.database_url

        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()