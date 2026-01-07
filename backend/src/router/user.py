import json
from typing import Callable

from fastapi import APIRouter, Response, status, Depends

from src.database import DatabaseSessionDepend
from src.exceptions import (
    ValidationError,
    InvalidCredentialsError,
    UserLockedError,
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
    login_token,
)
from src.util.auth import verify_auth_token

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


@router.get("/user/me/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(user=Depends(verify_auth_token)):
    return UserResponse(
        id=user.id, username=user.username, name=user.name, email=user.email
    )
