"""
The Bestory Project
"""

from tbs.lib import exceptions
from tbs.lib import utils
from tbs.models import User


async def create(user):
    """Create a new session JWT."""
    return utils.jwt.encode({
        "user": {
            "id": user.id
        }
    })


def login_required(fn):
    async def wrapper(root, info, *args, **kwargs):
        if info.context["request"]["session"]["user"] is None:
            raise exceptions.TheBestoryError("Login required")
        else:
            return await fn(root, info, **kwargs)

    return wrapper


async def request_middleware(request):
    """Decodes a session JWT from the request."""
    request["session"] = {
        "user": None,
        "jwt": None
    }

    authorization = request.headers.get('Authorization', None)
    if authorization is None:
        return

    # Skip incorrect request header value
    # Header format is "Bearer <JWT>"
    try:
        jwt = authorization.split()[-1]
    except IndexError:
        return

    request["session"]["jwt"] = jwt

    try:
        claims = utils.jwt.decode(jwt)
    except exceptions.JWTError:
        return

    try:
        user = await User.get(id=claims["pld"]["user"]["id"])
    except (KeyError, exceptions.DatabaseError):
        return

    request["session"]["user"] = user
