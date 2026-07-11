from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DAYPLAY_")

    sqlite_name: str = "database.db"
    debug: bool = False
    root_path: str = "/api/v1"

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_name}"


settings = Settings()
