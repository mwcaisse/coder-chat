from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from src.exceptions import InvalidTokenError
from src.services.user import validate_user_access_token

bearer_security = HTTPBearer()


def verify_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
):
    try:
        return validate_user_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
