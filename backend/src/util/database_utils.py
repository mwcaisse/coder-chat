from sqlalchemy import URL

from src.config_models import DatabaseSettings


def create_database_connection_url(db_settings: DatabaseSettings) -> URL:
    return URL.create(
        "postgresql+psycopg2",
        username=db_settings.user,
        password=db_settings.password,
        host=db_settings.host,
        database=db_settings.database,
        port=db_settings.port,
    )
