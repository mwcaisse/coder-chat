from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.config import Config
from fastapi import Depends
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session

from src.config import CONFIG
from src.logs import get_logger
from src.util.database_utils import create_database_connection_url

logger = get_logger(__name__)


def get_database_session():
    db_url = create_database_connection_url(CONFIG.db)
    engine = create_engine(db_url)
    with Session(engine) as session:
        yield session


DatabaseSessionDepend = Annotated[Session, Depends(get_database_session)]


def run_database_migrations(db_url: URL = None):
    try:
        logger.info("Starting database migrations")
        if db_url is None:
            db_url = create_database_connection_url(CONFIG.db)

        project_root_path = Path(__file__).parents[1].absolute()
        config_path = str(project_root_path.joinpath("alembic.ini"))
        logger.info("Using configuration from %s", config_path)

        alembic_config = Config(config_path)
        database_url = db_url.render_as_string(hide_password=False)
        database_url = database_url.replace("%", "%%")
        alembic_config.set_main_option("sqlalchemy.url", database_url)
        alembic_config.set_main_option("configure_logging", "false")

        alembic_script_location = alembic_config.get_main_option("script_location")
        if alembic_script_location is None:
            raise ValueError("Alembic: `script_location` must be specified.")

        alembic_config.set_main_option(
            "script_location", str(project_root_path.joinpath(alembic_script_location))
        )
        command.upgrade(alembic_config, "head")
    except Exception:
        logger.exception("Failed to perform database migrations")
        raise

    logger.info("Successfully updated database")
