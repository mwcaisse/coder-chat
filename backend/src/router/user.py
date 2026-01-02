import json
from typing import Annotated

from fastapi import APIRouter, Response, status, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from src.database import DatabaseSessionDepend
from src.exceptions import (
    ValidationError,
    InvalidCredentialsError,
    UserLockedError,
    InvalidTokenError,
)
from src.models.user import (
    CreateNewUserModel,
    UserLoginModel,
    UserLoginResponse,
    UserResponse,
)
from src.services.user import create_user, login, validate_user_access_token

router = APIRouter()


@router.post("/user/")
def create_user_r(user: CreateNewUserModel, db: DatabaseSessionDepend):
    try:
        create_user(user, db)
        return Response(status_code=status.HTTP_201_CREATED)

    except ValidationError as e:
        # TODO: This should be an app wide handler / middleware, but this works for now
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=json.dumps({"error": str(e)}),
        )


@router.post(
    "/user/login/", response_model=UserLoginResponse, status_code=status.HTTP_200_OK
)
def login_r(user_login: UserLoginModel, db: DatabaseSessionDepend):
    try:
        return login(user_login, db)

    except InvalidCredentialsError:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.dumps({"error": "Invalid username or password"}),
        )

    except UserLockedError:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.dumps({"error": "Account is currently locked"}),
        )


bearer_security = HTTPBearer()


@router.get("/user/me/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)]):
    try:
        user = validate_user_access_token(credentials.credentials)
        return UserResponse(
            id=user.id, username=user.username, name=user.name, email=user.email
        )
    except InvalidTokenError:
        raise bearer_security.make_not_authenticated_error()
