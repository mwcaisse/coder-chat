from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine

from src.config_models import DatabaseSettings
from src.data_models.base import CoderChatBaseModel  # noqa
from src.data_models.all_metadata import *  # noqa

from src.util.database_utils import create_database_connection_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


configure_logging = (
    config.get_main_option("configure_logging", "true").lower() == "true"
)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if configure_logging and config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = CoderChatBaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Load up any env vars from a .env
load_dotenv(".env")


class AlembicSettings(BaseSettings):
    """
    Stripped down version of pydantic BaseSettings to support loading in the database configuration from ENV vars
    """

    model_config = SettingsConfigDict(env_prefix="CC_", env_nested_delimiter="_")

    db: DatabaseSettings


ALEMBIC_CONFIG = AlembicSettings()


def get_database_url():
    sqlalchemy_url_option = config.get_main_option("sqlalchemy.url", None)
    if sqlalchemy_url_option is not None:
        return sqlalchemy_url_option

    return create_database_connection_url(ALEMBIC_CONFIG.db)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(get_database_url())

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
