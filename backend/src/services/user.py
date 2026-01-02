import secrets
import uuid
import datetime
from typing import NamedTuple

import argon2
import jwt
from argon2 import PasswordHasher
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from src.config import CONFIG
from src.data_models.user import User, UserRefreshToken
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
    UserTokenLoginModel,
)


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


def _validate_login_user(username: str, db: Session) -> User:
    user_query = select(User).select_from(User).where(User.username == username.lower())
    user = db.scalars(user_query).first()

    if user is None:
        # Validate the password, so this function takes the same amount of time if the user does not exist as if it does
        _verify_password(FAKE_HASH, username)
        raise InvalidCredentialsError()

    if user.locked:
        raise UserLockedError()

    return user


def _create_login_response_for_user(user: User, db: Session) -> UserLoginResponse:
    return UserLoginResponse(
        access_token=_create_user_access_token(user),
        refresh_token=_create_refresh_token(user.id, db),
    )


def login(login_model: UserLoginModel, db: Session) -> UserLoginResponse:
    user = _validate_login_user(login_model.username, db)

    if not _verify_password(user.password, login_model.password):
        raise InvalidCredentialsError()

    return _create_login_response_for_user(user, db)


def login_token(login_model: UserTokenLoginModel, db: Session) -> UserLoginResponse:
    user = _validate_login_user(login_model.username, db)

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    token_prefix = login_model.refresh_token[:16]
    provided_token = login_model.refresh_token[16:]

    token_query = (
        select(UserRefreshToken)
        .select_from(UserRefreshToken)
        .where(
            and_(
                UserRefreshToken.user_id == user.id,
                UserRefreshToken.token_prefix == token_prefix,
                UserRefreshToken.expire_date > now,
            )
        )
    )
    token = db.scalars(token_query).first()

    if token is None:
        raise InvalidCredentialsError()

    if not _verify_password(token.token_hash, provided_token):
        raise InvalidCredentialsError()

    # we've consumed the token, delete it
    db.delete(token)
    db.commit()

    return _create_login_response_for_user(user, db)


class JwtUser(NamedTuple):
    id: uuid.UUID
    username: str
    name: str
    email: str


JWT_SIGN_ALGO = "HS256"


def _create_user_access_token(user: User) -> str:
    """
    Creates an access token (JWT) for the given user

    :param user:
    :return:
    """

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    payload = {
        "iat": now,
        "nbf": now,
        "exp": now + datetime.timedelta(minutes=60),
        "sub": str(user.id),
        "username": user.username,
        "name": user.name,
        "email": user.email,
    }
    return jwt.encode(payload, CONFIG.jwt_sign_secret, algorithm=JWT_SIGN_ALGO)


def validate_user_access_token(token: str) -> JwtUser:
    try:
        decoded_payload = jwt.decode(
            token,
            CONFIG.jwt_sign_secret,
            algorithms=[JWT_SIGN_ALGO],
            options={
                "require": ["iat", "nbf", "exp", "sub", "username", "name", "email"]
            },
        )
        return JwtUser(
            id=uuid.UUID(decoded_payload["sub"]),
            username=decoded_payload["username"],
            name=decoded_payload["name"],
            email=decoded_payload["email"],
        )
    except jwt.PyJWTError:
        raise InvalidTokenError()


def _generate_refresh_token() -> tuple[str, str]:
    return secrets.token_urlsafe(16)[:16], secrets.token_urlsafe(128)


def _create_refresh_token(user_id: uuid.UUID, db: Session) -> str:
    """
    Creates a refresh token for the user with the given user id
    :param user_id:
    :return:
    """
    token_prefix, token = _generate_refresh_token()
    token_hash = _hash_password(token)

    db.add(
        UserRefreshToken(
            user_id=user_id,
            token_prefix=token_prefix,
            token_hash=token_hash,
            expire_date=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=7),
        )
    )
    db.commit()

    return f"{token_prefix}{token}"
