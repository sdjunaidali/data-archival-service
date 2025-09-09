from typing import Tuple, Type
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    secret_key: str = Field(..., alias="SECRET_KEY")
    source_database_url: PostgresDsn = Field(..., alias="SOURCE_DATABASE_URL")
    archive_database_url: PostgresDsn = Field(..., alias="ARCHIVE_DATABASE_URL")
    celery_broker_url: str = Field(..., alias="CELERY_BROKER_URL")
    debug: bool = Field(default=False, alias="DEBUG")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Priority: environment > init kwargs > .env > file secrets
        return (env_settings, init_settings, dotenv_settings, file_secret_settings)

settings = Settings()