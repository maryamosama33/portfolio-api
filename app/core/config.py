from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    db_name: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
