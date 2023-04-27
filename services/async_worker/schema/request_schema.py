from pydantic import BaseModel
from typing import Optional, List


class AlikeSearchRequest(BaseModel):
    phrase: Optional[str]