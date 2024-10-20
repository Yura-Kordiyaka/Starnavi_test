from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class DB_Settings(BaseSettings):
    DB_HOST: str = os.environ.get('DB_HOST')
    DB_PORT: int = os.environ.get('DB_PORT')
    DB_USER: str = os.environ.get('DB_USER')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD')
    DB_NAME: str = os.environ.get('DB_NAME')

    DB_TEST_HOST: str = os.environ.get('DB_TEST_HOST')
    DB_TEST_PORT: int = os.environ.get('DB_TEST_PORT')
    DB_TEST_USER: str = os.environ.get('DB_TEST_USER')
    DB_TEST_PASSWORD: str = os.environ.get('DB_TEST_PASSWORD')
    DB_TEST_NAME: str = os.environ.get('DB_TEST_NAME')



class TokenSettings(BaseSettings):
    ALGORITHM: str = os.environ.get('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.environ.get('REFRESH_TOKEN_EXPIRE_MINUTES')
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY')
    JWT_REFRESH_SECRET_KEY: str = os.environ.get('JWT_REFRESH_SECRET_KEY')


class GoogleSettings(BaseSettings):
    AI_API_KEY: str = os.environ.get('AI_API_KEY')


class Settings(BaseSettings):
    db: DB_Settings = DB_Settings()
    token: TokenSettings = TokenSettings()
    google: GoogleSettings = GoogleSettings()


settings = Settings()
