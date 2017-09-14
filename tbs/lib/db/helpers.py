"""
The Bestory Project
"""

from functools import wraps

from asyncpg.connection import Connection

from tbs import db_connection


def provide_connection(fn):
    async def wrapper(*args, conn: Connection=None, **kwargs):
        if conn is None:
            async with db_connection.pool.acquire() as conn:
                return await fn(*args, **kwargs, conn=conn)
        return await fn(*args, **kwargs, conn=conn)

    return wrapper
