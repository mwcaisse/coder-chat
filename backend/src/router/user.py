import json

from fastapi import APIRouter, Response, status

from src.database import DatabaseSessionDepend
from src.exceptions import ValidationError
from src.models.user import CreateNewUserModel
from src.services.user import create_user

router = APIRouter()


@router.post("/user/")
def create_user_r(user: CreateNewUserModel, db: DatabaseSessionDepend):
    try:
        create_user(user, db)
    except ValidationError as e:
        # TODO: This should be an app wide handler / middleware, but this works for now
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=json.dumps({"error": str(e)}),
        )

    return Response(status_code=status.HTTP_201_CREATED)
