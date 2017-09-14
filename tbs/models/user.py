"""
The Bestory Project
"""

import re
from datetime import datetime

import pendulum
from asyncpg.connection import Connection

from tbs.lib import utils
from tbs.lib.db import schema
from tbs.lib.db.node import SnowflakeNode
from tbs.lib.model import DateTime, Integer, String
from tbs.lib.model.base import validator


class User(SnowflakeNode):
    """User model and DB representation."""

    SCHEMA = schema.users
    SNOWFLAKE_TYPE = "user"

    # id = Snowflake(...)

    username = String(max_length=32, nullable=False)
    nickname = String(max_length=64, nullable=False)
    password = String(max_length=255, nullable=False)

    posts_count = Integer(minimum=0, default=0, nullable=False)
    likes_count = Integer(minimum=0, default=0, nullable=False)

    registered_at = DateTime(
        default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
        nullable=False)

    @validator(username)
    def validate_username(self, username: str):
        if re.match(r"^[a-zA-Z0-9_.-]+$", username) is None:
            raise ValueError("Username can contains only a-z "
                "letters, digits, dashes, dots and underscores")

    @classmethod
    async def get_by_username(cls, username: str, conn: Connection=None):
        """Get a single user by it's username."""
        query = cls.SCHEMA.select().where(cls.SCHEMA.c.username == username)
        return await super().get(conn=conn, query=query)

    @classmethod
    async def list(cls,
                   conn: Connection=None,
                   query=None):
        """List users."""
        if query is None:
            query = cls.SCHEMA.select().order_by(
                cls.SCHEMA.c.registered_at.desc())

        return await super().list(conn=conn, query=query)

    async def save(self, conn: Connection=None, **kwargs):
        """Save user."""
        if type(self).password in self.META.changed:
            self.password = utils.password.hash(self.password)

        return await super().save(conn=conn, **kwargs)

    async def increment_posts_counter(self, conn: Connection=None):
        """Increment posts counter of the user."""
        return await self.save(conn=conn,
            posts_count=self.SCHEMA.c.posts_count + 1)

    async def increment_likes_counter(self, conn: Connection=None):
        """Increment likes counter of the user."""
        return await self.save(conn=conn,
            likes_count=self.SCHEMA.c.likes_count + 1)

    async def decrement_posts_counter(self, conn: Connection=None):
        """Decrement posts counter of the user."""
        return await self.save(conn=conn,
            posts_count=self.SCHEMA.c.posts_count - 1)

    async def decrement_likes_counter(self, conn: Connection=None):
        """Decrement likes counter of the user."""
        return await self.save(conn=conn,
            likes_count=self.SCHEMA.c.likes_count - 1)
