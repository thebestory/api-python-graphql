"""
The Bestory Project
"""

from datetime import datetime
from typing import List

import pendulum
from asyncpg.connection import Connection
from sqlalchemy.sql.expression import func

from tbs.lib.db import helpers
from tbs.lib.db import schema
from tbs.lib.db.node import SnowflakeNode
from tbs.lib.model.types import Boolean, DateTime, Integer, Snowflake, String
from tbs.models.topic import Topic
from tbs.models.user import User


class Post(SnowflakeNode):
    """Post model and DB representation."""

    SCHEMA = schema.posts
    SNOWFLAKE_TYPE = "post"

    # id = Snowflake(...)

    author_id = Snowflake(nullable=False)
    parent_id = Snowflake(nullable=False)
    content = String(max_length=8196, nullable=False)

    responses_count = Integer(minimum=0, default=0, nullable=False)
    likes_count = Integer(minimum=0, default=0, nullable=False)

    is_published = Boolean(default=False, nullable=False)
    is_removed = Boolean(default=False, nullable=False)

    submitted_at = DateTime(
        default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
        nullable=False)
    published_at = DateTime(
        default=lambda: datetime.utcnow().replace(tzinfo=pendulum.UTC),
        nullable=False)
    edited_at = DateTime(nullable=True)

    # TODO: Memoize
    @property
    async def author(self):
        return await User.get(id=self.author_id)

    # TODO: Memoize
    @property
    async def topic(self):
        return await Topic.get(id=self.topic_id)

    @classmethod
    async def list(cls,
                   authors: List[int]=None,
                   inverse_authors: bool=False,
                   parents: List[int]=None,
                   inverse_parents: bool=False,
                   topics: List[int]=None,
                   inverse_topics: bool=False,
                   submitted_at_before: datetime=None,
                   submitted_at_after: datetime=None,
                   published_at_before: datetime=None,
                   published_at_after: datetime=None,
                   edited_at_before: datetime=None,
                   edited_at_after: datetime=None,
                   is_published: bool=None,
                   is_removed: bool=None,
                   is_edited: bool=None,
                   conn: Connection=None,
                   query=None):
        """List stories."""
        if submitted_at_before is not None and submitted_at_after is not None:
            raise ValueError("Only one of `submitted_date_before` and "
                            "`submitted_date_after` can be specified")

        if published_at_before is not None and published_at_after is not None:
            raise ValueError("Only one of `published_date_before` and "
                            "`published_date_after` can be specified")

        if edited_at_before is not None and edited_at_after is not None:
            raise ValueError("Only one of `edited_date_before` and "
                            "`edited_date_after` can be specified")

        if query is None:
            query = cls.SCHEMA.select()

        if authors is None or len(authors) == 0:
            inverse_authors = True
        elif inverse_authors:
            query = query.where(~cls.SCHEMA.c.author_id.in_(authors))
        else:
            query = query.where(cls.SCHEMA.c.author_id.in_(authors))

        if parents is None or len(parents) == 0:
            inverse_parents = True
        elif inverse_parents:
            query = query.where(~cls.SCHEMA.c.parent_id.in_(parents))
        else:
            query = query.where(cls.SCHEMA.c.parent_id.in_(parents))

        if topics is None or len(topics) == 0:
            inverse_topics = True
        elif inverse_topics:
            query = query.where(~cls.SCHEMA.c.topic_id.in_(topics))
        else:
            query = query.where(cls.SCHEMA.c.topic_id.in_(topics))

        if submitted_at_before is not None:
            query = query.where(
                cls.SCHEMA.c.submitted_at < submitted_at_before)
        if submitted_at_after is not None:
            query = query.where(
                cls.SCHEMA.c.submitted_at > submitted_at_after)

        if published_at_before is not None:
            query = query.where(
                cls.SCHEMA.c.published_at < published_at_before)
        if published_at_after is not None:
            query = query.where(
                cls.SCHEMA.c.published_at > published_at_after)

        if edited_at_before is not None:
            query = query.where(
                cls.SCHEMA.c.edited_at < edited_at_before)
        if edited_at_after is not None:
            query = query.where(
                cls.SCHEMA.c.edited_at > edited_at_after)

        if is_published is not None:
            query = query.where(cls.SCHEMA.c.is_published == is_published)
        if is_removed is not None:
            query = query.where(cls.SCHEMA.c.is_removed == is_removed)
        if is_edited is not None:
            if is_edited:
                query = query.where(cls.SCHEMA.c.edited_at != None)
            else:
                query = query.where(cls.SCHEMA.c.edited_at == None)

        return await super().list(conn=conn, query=query)

    @classmethod
    async def list_latest(cls, conn: Connection=None, *args, **kwargs) -> list:
        """List latest stories."""
        query = cls.SCHEMA.select().order_by(cls.SCHEMA.c.published_at.desc())
        return await cls.list(conn=conn, query=query, *args, **kwargs)

    @classmethod
    async def list_top(cls, conn: Connection=None, *args, **kwargs) -> list:
        """List top stories."""
        query = cls.SCHEMA.select()
        query = query.order_by(cls.SCHEMA.c.reactions_count.desc())
        query = query.order_by(cls.SCHEMA.c.published_at.desc())
        return await cls.list(conn=conn, query=query, *args, **kwargs)

    @classmethod
    async def list_hot(cls, conn: Connection=None, *args, **kwargs) -> list:
        """List hot stories."""
        return await cls.list_top(conn=conn, *args, **kwargs)

    @classmethod
    async def list_random(cls, conn: Connection=None, *args, **kwargs) -> list:
        """List hot stories."""
        query = cls.SCHEMA.select().order_by(func.random())
        return await cls.list(conn=conn, query=query, *args, **kwargs)

    @helpers.provide_connection
    async def save(self, conn: Connection, **kwargs):
        """Save story."""
        if not self.META.saved:
            async with conn.transaction():
                res = await super().save(conn=conn, **kwargs)
                await (await self.author).increment_stories_counter()
                await (await self.topic).increment_stories_counter()
                return res
        else:
            if type(self).content in self.META.changed:
                self.edited_at = datetime.utcnow().replace(tzinfo=pendulum.UTC)
            if type(self).is_published in self.META.changed:
                self.published_at = datetime.utcnow().replace(
                    tzinfo=pendulum.UTC)

            return await super().save(conn=conn, **kwargs)

    async def increment_comments_counter(self, conn: Connection=None):
        """Increment comments counter of the story."""
        return await self.save(conn=conn,
            comments_count=self.SCHEMA.c.comments_count + 1)

    async def increment_reactions_counter(self, conn: Connection=None):
        """Increment reactions counter of the story."""
        return await self.save(conn=conn,
            reactions_count=self.SCHEMA.c.reactions_count + 1)

    async def decrement_comments_counter(self, conn: Connection=None):
        """Decrement comments counter of the story."""
        return await self.save(conn=conn,
            comments_count=self.SCHEMA.c.comments_count - 1)

    async def decrement_reactions_counter(self, conn: Connection=None):
        """Decrement reactions counter of the story."""
        return await self.save(conn=conn,
            reactions_count=self.SCHEMA.c.reactions_count - 1)

    async def delete(self, conn: Connection=None):
        """Delete the story."""
        if self.META.saved:
            res = await self.save(conn=conn, is_removed=True)
            self.is_removed = True
            return res

        return None
