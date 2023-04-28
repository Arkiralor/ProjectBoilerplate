from datetime import datetime, timedelta
from fastapi import status, HTTPException
from typing import Optional
from jose import JWTError, jwt

from auth.schema import TokenData
from config.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)



def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate token',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get('user_id')
                
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(**payload)
        return token_data
    except JWTError:
        raise credentials_exception