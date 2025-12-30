from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config import CONFIG
from src.util.database_utils import create_database_connection_url


def get_database_session():
    db_url = create_database_connection_url(CONFIG.db)
    engine = create_engine(db_url)
    with Session(engine) as session:
        yield session
