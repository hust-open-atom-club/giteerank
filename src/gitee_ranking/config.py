from functools import lru_cache

from dotenv import find_dotenv
from pydantic_settings import BaseSettings


@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    email: str
    password: str
    client_id: str
    client_secret: str
    webhook_url: str
    groups_str: str
    start_hour: int = 9

    class Config:
        env_file = find_dotenv()


settings = get_settings()
