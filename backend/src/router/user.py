import json
from typing import Annotated, Callable

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
    UserTokenLoginModel,
)
from src.services.user import (
    create_user,
    login,
    validate_user_access_token,
    login_token,
)

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


def _perform_login(login_fun: Callable[[], UserLoginResponse]):
    try:
        return login_fun()

    except InvalidCredentialsError:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.dumps({"error": "Invalid username or credentials"}),
        )

    except UserLockedError:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.dumps({"error": "Account is currently locked"}),
        )


@router.post(
    "/user/login/", response_model=UserLoginResponse, status_code=status.HTTP_200_OK
)
def login_r(user_login: UserLoginModel, db: DatabaseSessionDepend):
    return _perform_login(lambda: login(user_login, db))


@router.post(
    "/user/login/token",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK,
)
def login_token_r(token_login: UserTokenLoginModel, db: DatabaseSessionDepend):
    return _perform_login(lambda: login_token(token_login, db))


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
