import secrets

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def generate_random_jwt_secret() -> str:
    return secrets.token_urlsafe(128)


class DatabaseSettings(BaseModel):
    """
    Settings module for database settings.

    Provide:
        * host: Hostname / IP Address of the database server
        * port: The database port. Defaults to `5432`
        * user: The user to log into the database with
        * password: The password for the user
        * database: The name of the database to connect to
    """

    host: str
    user: str
    password: str
    database: str

    port: int = 5432


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CC_", env_nested_delimiter="_")

    model_path: str

    serve_static_files: bool = True
    static_directory: str = "static"

    db: DatabaseSettings

    jwt_sign_secret: str = generate_random_jwt_secret()
