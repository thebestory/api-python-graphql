"""
The Bestory Project
"""

import pendulum
from jose import jwt
from jose.exceptions import JWTError

from tbs.config import jose as config
from tbs.lib import exceptions


def encode(payload: dict) -> str:
    """Create a new JWT."""
    # aud = audience.value
    iat = pendulum.utcnow().int_timestamp
    nbf = iat
    exp = iat + config.EXPIRATION_DELTA

    try:
        return jwt.encode(
            {
                "iss": config.ISSUER,
                # "aud": audience,

                "iat": iat,
                "nbf": nbf,
                "exp": exp,

                "pld": payload,
            },
            config.SECRET,
            config.ALGORITHM
        )
    except JWTError:
        raise exceptions.JWTError


def verify(token: str) -> bool:
    """Verify the JWT."""
    try:
        claims = jwt.decode(token, config.SECRET, config.ALGORITHM)
        return True
    except JWTError:
        return False


def decode(token: str, verify: bool=True) -> dict:
    """Decode the JWT."""
    if verify:
        try:
            return jwt.decode(token, config.SECRET, config.ALGORITHM)
        except JWTError:
            raise exceptions.JWTError
    else:
        return jwt.get_unverified_claims(token)
