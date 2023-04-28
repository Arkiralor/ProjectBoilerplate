from pydantic import BaseModel

class TokenData(BaseModel):
    """
    Schema to contain information regarding JWT Token with the following payload:
        token_type: str
        exp: timestamp
        iat: timestamp
        jti: str
        user_id: str
    """
    token_type: str
    exp: int
    iat: int
    jti: str
    user_id: str

class UserData(BaseModel):
    """
    Schema to output user information with the following payload in a response, should required.
    """
    id: str
    username: str
    email: str
    date_joined: str
    last_login: str
    is_staff: bool
    is_superuser: bool