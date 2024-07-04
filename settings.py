from pydantic_settings import BaseSettings  # noqa F401


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_service: str
    postgres_port: int

    class Config:
        env_file = ".env"


settings = Settings()
