"""
The Bestory Project
"""

import re

from asyncpg.connection import Connection

from tbs.lib.db import helpers
from tbs.lib.db import schema
from tbs.lib.db.node import SnowflakeNode
from tbs.lib.model.base import validator
from tbs.lib.model.types import Boolean, Integer, String


class Topic(SnowflakeNode):
    """Topic model and DB representation."""

    SCHEMA = schema.topics
    SNOWFLAKE_TYPE = "topic"

    # id = Snowflake(...)

    title = String(max_length=64, nullable=False)
    slug = String(max_length=32, nullable=False)
    description = String(max_length=512, nullable=False)

    posts_count = Integer(minimum=0, default=0, nullable=False)

    is_active = Boolean(default=False, nullable=False)

    @validator(slug)
    def validate_slug(self, slug: str):
        if re.match(r"^[a-z]+[a-z0-9]*$", slug) is None:
            raise ValueError("Slug must contains only a-z "
                "letters and digits, and starts with letter")

    @classmethod
    async def list(cls, is_active: bool=None, conn: Connection=None) -> list:
        """List topics."""
        query = cls.SCHEMA.select().order_by(cls.SCHEMA.c.title)

        if is_active is not None:
            query = query.where(cls.SCHEMA.c.is_active == is_active)

        return await super().list(conn=conn, query=query)

    @classmethod
    async def get_by_slug(cls, slug: str, conn: Connection=None):
        """Get a single topic by it's slug."""
        query = cls.SCHEMA.select().where(cls.SCHEMA.c.slug == slug)
        return await super().get(conn=conn, query=query)

    async def increment_posts_counter(self, conn: Connection=None):
        """Increment posts counter of the topic."""
        return await self.save(conn=conn, 
            posts_count=self.SCHEMA.c.posts_count + 1)

    async def decrement_posts_counter(self, conn: Connection=None):
        """Decrement posts counter of the topic."""
        return await self.save(conn=conn, 
            posts_count=self.SCHEMA.c.posts_count - 1)
