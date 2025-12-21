from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CC_")

    model_path: str

    serve_static_files: bool = True
    static_directory: str = "static"


CONFIG = ApplicationSettings()
