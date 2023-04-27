from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class AuthorSearchResponse(BaseModel):
    id: str = Field(alias='_id')
    username: str
    email: str


class StoryResponse(BaseModel):
    id: str = Field(alias='_id')
    title: str
    blurb: str
    author: AuthorSearchResponse
    tags: Optional[List[str]]
    created: datetime
    updated: datetime


class AlikeSearchResponse(BaseModel):
    story: StoryResponse
    confidence: str
