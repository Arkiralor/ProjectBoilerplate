"""
Relational Databases are not usually required in this microservice,
but we require some relational models to handle some functionality.
"""

from sqlmodel import create_engine

from config.settings import settings

engine = create_engine(settings.DB_URI, echo=True)

## Done, we don't need to create the tables here as we already manage the tables from the monolithic backend repository.