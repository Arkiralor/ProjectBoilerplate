from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default=None, primary_key=True)
    username: str
    email: str
    date_joined: datetime