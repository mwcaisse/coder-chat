from fastapi import APIRouter

from src.database import DatabaseSessionDepend
from src.models.user import CreateNewUserModel
from src.services.user import create_user

router = APIRouter()


@router.post("/user/")
def create_user_r(user: CreateNewUserModel, db: DatabaseSessionDepend):
    create_user(user, db)
