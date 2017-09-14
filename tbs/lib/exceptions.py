"""
The Bestory Project
"""

from jose.exceptions import JWTError


class TheBestoryError(Exception):
    pass


class JWTError(TheBestoryError, JWTError):
    pass


class DatabaseError(TheBestoryError):
    pass


class NotFetchedError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class NotSavedError(DatabaseError):
    pass


class NotCreatedError(NotSavedError):
    pass


class NotUpdatedError(NotSavedError):
    pass
