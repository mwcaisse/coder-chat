class ValidationError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UserLockedError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass
