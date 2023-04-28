"""
Relational Databases are not usually required in this microservice,
but we require some relational models to handle some functionality.
"""
from config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import DeclarativeBase


engine = create_engine(settings.DB_URI, encoding='utf-8', echo=True)


class BaseSQLModel(DeclarativeBase):
    pass


def get_session(engine=engine):
    """
    This function returns a session to the database.
    """
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return session
