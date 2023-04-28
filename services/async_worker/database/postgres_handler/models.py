from datetime import datetime
from typing import Optional
from uuid import UUID as UUIDClass

from sqlalchemy import Table, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import settings
from database.postgres_handler import engine, BaseSQLModel


class User(BaseSQLModel):
    """
    Database table to contain USER information.

    NOTE: This table will NEVER be created/updated/deleted from the `ASYNC_WORKER` service.
    It only exists so that the service can retrieve user information from the main database after decrypting the JWT Token.
    """
    
    __tablename__ = settings.USER_TABLE

    id: Mapped[UUIDClass] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(16),unique=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    date_joined: Mapped[datetime] = mapped_column(DateTime())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime())
    is_staff: Mapped[bool] = mapped_column(Boolean())
    is_superuser: Mapped[bool] = mapped_column(Boolean())

    def __init__(self, id: UUIDClass, username: str, email: str, date_joined: datetime, last_login: datetime, is_staff: bool, is_superuser: bool) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.date_joined = date_joined
        self.last_login = last_login
        self.is_staff = is_staff
        self.is_superuser = is_superuser

    def __repr__(self) -> str:
        return self.email
    
    def __str__(self) -> str:
        return self.email
    


