from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://dev:dev_password@localhost:5432/myapp_dev"

    class Config:
        env_file = ".env"


settings = Settings()