
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    DEBUG: bool = False
    model_config = SettingsConfigDict(env_file=".env")
    mongo_connection: SecretStr
    resend_token: SecretStr

CONFIG = Settings()
