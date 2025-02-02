from pydantic_settings import BaseSettings, SettingsConfigDict




class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        extra="ignore"
    )


settings = Settings()