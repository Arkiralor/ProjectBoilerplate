from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select

from auth.jwt import verify_token
from database.postgres_handler.models import User
from database.postgres_handler import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate token',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    session = get_session()

    try:
        token_data = verify_token(token=token)
        user = session.execute(select(User).where(
            User.id == token_data.user_id)).scalar_one_or_none()
        if not user:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception
