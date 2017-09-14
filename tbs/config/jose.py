"""
The Bestory Project
"""

ALGORITHM = "HS256"
SECRET = "thebestory"

ISSUER = "The Bestory"

# Defaults to 3 month
# Client can refresh token is needed before expiration date
EXPIRATION_DELTA = 60 * 60 * 24 * 30 * 3
