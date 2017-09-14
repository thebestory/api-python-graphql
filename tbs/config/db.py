"""
The Bestory Project
"""

# Default connection parameters are set
# according to the Docker environment
HOST = "postgres"
PORT = 5432
USER = "postgres"
PASSWORD = ""
DATABASE = "postgres"

POOL_MIN_SIZE = 5
POOL_MAX_SIZE = 10

MAX_QUERIES = 50000
MAX_INACTIVE_CONNECTION_LIFETIME = 300.0
