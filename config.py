from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ASCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_nested_delimiters = "__"

setting = Settings(_env_file = os.path.join(os.getcwd(), "ToDo-Webapp/.env"))