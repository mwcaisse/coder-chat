import json

from fastapi import APIRouter, Response, status

from src.database import DatabaseSessionDepend
from src.exceptions import ValidationError, InvalidCredentialsError, UserLockedError
from src.models.user import CreateNewUserModel, UserLoginModel
from src.services.user import create_user, login

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


@router.post("/user/login/")
def login_r(user_login: UserLoginModel, db: DatabaseSessionDepend):
    try:
        login(user_login, db)
        return Response(status_code=status.HTTP_200_OK)

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
