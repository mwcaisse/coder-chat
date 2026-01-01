import json

import argon2
from argon2 import PasswordHasher
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.data_models.user import User
from src.exceptions import ValidationError, InvalidCredentialsError, UserLockedError
from src.models.user import CreateNewUserModel, UserLoginModel


def _throw_if_already_exists(user: CreateNewUserModel, db: Session):
    """
        If a user with the given username or email already exists, raise a ValidationError

    :param user: The user that is being created
    :param db: The database session
    :return:
    """
    existing_user_query = (
        select(User)
        .select_from(User)
        .where(or_(User.username == user.username, User.email == user.email))
    )
    existing_user = db.scalars(existing_user_query).first()

    if existing_user is not None:
        raise ValidationError("User with given username or email already exists")


_PASSWORD_HASHER = PasswordHasher()
FAKE_HASH = _PASSWORD_HASHER.hash("fake_password")


def _hash_password(password: str) -> str:
    """
    Returns the hash of the given password

    :param password:
    :return:
    """
    return _PASSWORD_HASHER.hash(password)


def _verify_password(hashed_password: str, password: str) -> bool:
    """
    Verifies the provided password against the hashed password

    :param hashed_password: The hashed password
    :param password: The raw password provided as input by the user
    :return: True if matches, false otherwise
    """
    try:
        return _PASSWORD_HASHER.verify(hashed_password, password)
    except argon2.exceptions.VerificationError:
        return False


def create_user(create_model: CreateNewUserModel, db: Session):
    """
    Create a new user

    :param create_model: The user to create
    :return:
    """

    # Check that a user with the given username or email does not already exist
    _throw_if_already_exists(create_model, db)

    user = User(
        username=create_model.username.lower(),
        email=create_model.email,
        password=_hash_password(create_model.password),
        name=create_model.name,
        locked=False,
    )
    db.add(user)
    db.commit()


def login(login_model: UserLoginModel, db: Session):
    user_query = (
        select(User)
        .select_from(User)
        .where(User.username == login_model.username.lower())
    )
    user = db.scalars(user_query).first()

    if user is None:
        _verify_password(FAKE_HASH, login_model.password)
        raise InvalidCredentialsError()

    if user.locked:
        raise UserLockedError()

    if not _verify_password(user.password, login_model.password):
        raise InvalidCredentialsError()
