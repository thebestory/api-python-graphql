"""
The Bestory Project
"""

from datetime import datetime
from typing import List

import pendulum
from asyncpg.connection import Connection

from tbs.lib.db import helpers
from tbs.lib.db import schema
from tbs.lib.db.node import Node, Snowflake
from tbs.lib.model.types import Boolean, DateTime
from tbs.lib.model.types import Snowflake as SnowflakeType
from tbs.models.post import Post
from tbs.models.user import User


class Like(Node):
    """Like model and DB representation."""

    SCHEMA = schema.likes

    user_id = SnowflakeType(nullable=False)
    post_id = SnowflakeType(nullable=False)

    submitted_at = DateTime(
        default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
        nullable=False)

    KEYS = ((user_id, SCHEMA.c.user_id), 
            (post_id, SCHEMA.c.post_id), )

    # TODO: Memoize
    @property
    async def user(self):
        return await User.get(id=self.user_id)

    # TODO: Memoize
    @property
    async def post(self):
        return await Post.get(id=self.post_id)

    @classmethod
    async def list(cls,
                   users: List[int]=None,
                   inverse_users: bool=False,
                   posts: List[int]=None,
                   inverse_posts: bool=False,
                   submitted_at_before: datetime=None,
                   submitted_at_after: datetime=None,
                   conn: Connection=None,
                   query=None):
        """List likes."""
        if submitted_at_before is not None and submitted_at_after is not None:
            raise ValueError("Only one of `submitted_date_before` and "
                            "`submitted_date_after` can be specified")

        if query is None:
            query = cls.SCHEMA.select()

        query = query.order_by(cls.SCHEMA.c.submitted_at.desc())
        query = query.order_by(cls.SCHEMA.c.user_id)
        query = query.order_by(cls.SCHEMA.c.post_id)

        if users is None or len(users) == 0:
            inverse_users = True
        elif inverse_users:
            query = query.where(~cls.SCHEMA.c.user_id.in_(users))
        else:
            query = query.where(cls.SCHEMA.c.user_id.in_(users))

        if posts is None or len(posts) == 0:
            inverse_posts = True
        elif inverse_posts:
            query = query.where(~cls.SCHEMA.c.post_id.in_(posts))
        else:
            query = query.where(cls.SCHEMA.c.post_id.in_(posts))

        if submitted_at_before is not None:
            query = query.where(
                cls.SCHEMA.c.submitted_at < submitted_at_before)
        if submitted_at_after is not None:
            query = query.where(
                cls.SCHEMA.c.submitted_at > submitted_at_after)

        return await super().list(conn=conn, query=query)

    @helpers.provide_connection
    async def save(self, conn: Connection, **kwargs):
        """Save like."""
        if not self.META.saved:
            async with conn.transaction():
                res = await super().save(conn=conn, **kwargs)
                await (await self.user).increment_likes_counter()
                await (await self.post).increment_likes_counter()
                return res
        else:
            return await super().save(conn=conn, **kwargs)

    @helpers.provide_connection
    async def delete(self, conn: Connection, query=None):
        """Delete the like."""
        if self.META.saved:
            async with conn.transaction():
                res = await super().delete(conn=conn, query=query)
                await (await self.user).decrement_likes_counter()
                await (await self.post).decrement_likes_counter()
                return res

        return None
