"""
The Bestory Project
"""

import os
import urllib.parse

from tbs.server import app, run


# Host and port within a local server

host = os.environ.get("HOST")
port = os.environ.get("PORT")

if host is not None:
    config.app.HOST = host

if port is not None:
    config.app.PORT = int(port)


# Machine ID for Snowflake ID generation

machine_id = os.environ.get("MACHINE_ID")

if machine_id is not None:
    config.snowflake.MACHINE_ID = int(machine_id)


# Database connection parameters

db = os.environ.get("DATABASE_URL")

if db is not None:
    db = urllib.parse.urlparse(db)

    config.db.HOST = db.hostname
    config.db.PORT = int(db.port)
    config.db.USER = db.username
    config.db.PASSWORD = db.password
    config.db.DATABASE = db.path[1:]


# Application starting

run()
