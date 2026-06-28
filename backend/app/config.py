from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://grocery_saver:grocery_saver@localhost:5432/grocery_saver"
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GROCERY_SAVER_")


settings = Settings()
