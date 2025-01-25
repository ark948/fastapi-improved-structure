from pydantic_settings import BaseSettings, SettingsConfigDict




class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        extra="ignore"
    )


settings = Settings()