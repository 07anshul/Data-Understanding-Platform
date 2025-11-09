from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    upload_folder: str = "uploads"
    output_folder: str = "outputs"

    class Config:
        env_file = "../../.env"
        env_file_encoding = "utf-8"

settings = Settings()