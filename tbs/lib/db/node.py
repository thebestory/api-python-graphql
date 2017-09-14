"""
The Bestory Project
"""

import asyncpgsa
import sqlalchemy as sa
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError

from tbs import db_connection
from tbs import snowflake_generator
from tbs.lib import exceptions
from tbs.lib.db import helpers
from tbs.lib.db import schema
from tbs.lib.model.base import Field, Meta, MetaInstance, Model
from tbs.lib.model.types import String
from tbs.lib.model.types import Snowflake as SnowflakeType


class NodeMetaInstance(MetaInstance):
    """Meta object, that contains information about the model, and
    model instance data, and also support ORM-like behaviour."""

    def __init__(self, meta: Meta, obj):
        self.changed = set()
        self.saved = False

        super().__init__(meta, obj)

    def set_changed(self, field: Field):
        """Set the changed flag to the field."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.changed |= {field}

    def unset_changed(self, field: Field):
        """Remove the changed flag from the field."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.changed -= {field}

    def set_changed_all(self):
        """Set the changed flag to all fields."""
        self.changed = self.fields.copy()

    def unset_changed_all(self):
        """Remove the changed flag from all fields."""
        self.changed = set()

    def set_value(self, field: Field, value):
        """Change the field value."""
        super().set_value(field, value)
        self.set_changed(field)


class Node(Model):
    """Abstract node / Database representation node."""

    SCHEMA: sa.Table
    """SQLAlchemy schema of node."""

    KEYS: tuple
    """List of database primary keys. Each key is a pair of model
    field and SQLAlchemy field."""

    def __init__(self, *args, **kwargs):
        meta = self.META
        meta_instance = NodeMetaInstance(meta, self)
        self.META = meta_instance

        for field in meta.fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    @classmethod
    @helpers.provide_connection
    async def list(cls, conn: Connection, query=None):
        """List objects."""
        if query is None:
            query = cls.SCHEMA.select()

        query, params = asyncpgsa.compile_query(query)

        try:
            rows = await conn.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        objs = []
        for row in rows:
            obj = cls(**cls.SCHEMA.parse(row))
            objs.append(obj)

            obj.META.unset_changed_all()
            obj.META.saved = True
            for field, _ in cls.KEYS:
                obj.META.lock(field)

        return objs

    @classmethod
    @helpers.provide_connection
    async def get(cls, conn: Connection, query=None, **kwargs):
        """Get a single object."""
        if query is None:
            query = cls.SCHEMA.select()

            for m_field, sa_field in cls.KEYS:
                if m_field.name not in kwargs:
                    raise AttributeError("Provide all needed primary keys")
                query = query.where(sa_field == kwargs[m_field.name])

        query, params = asyncpgsa.compile_query(query)

        try:
            row = await conn.fetchrow(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        if not row:
            raise exceptions.NotFoundError
        obj = cls(**cls.SCHEMA.parse(row))

        obj.META.unset_changed_all()
        obj.META.saved = True
        for field, _ in cls.KEYS:
            obj.META.lock(field)

        return obj

    @helpers.provide_connection
    async def save(self, conn: Connection, **kwargs):
        """Save object to the DB."""
        self.META.validate()

        if not self.META.saved:
            query = self.SCHEMA.insert()
        else:
            query = self.SCHEMA.update()

            for m_field, sa_field in self.KEYS:
                query = query.where(sa_field == getattr(self, m_field.name))

        for field in self.META.changed:
            query = query.values({field.name: getattr(self, field.name)})

        for field in kwargs:
            query = query.values({field: kwargs[field]})

        query, params = asyncpgsa.compile_query(query)

        try:
            await conn.execute(query, *params)
            self.META.unset_changed_all()

            if not self.META.saved:
                self.META.saved = True
                for field, _ in self.KEYS:
                    self.META.lock(field)
        except (PostgresError, exceptions.DatabaseError):
            # Object discarded from the DB due to exception
            if self.META.saved:
                raise exceptions.NotUpdatedError
            else:
                raise exceptions.NotCreatedError

    @classmethod
    @helpers.provide_connection
    async def delete(cls, conn: Connection, query=None, **kwargs):
        """Delete a single object."""
        if query is None:
            query = cls.SCHEMA.delete()

            for m_field, sa_field in cls.KEYS:
                if m_field.name not in kwargs:
                    raise AttributeError("Provide all needed primary keys")
                query = query.where(sa_field == kwargs[m_field.name])

        query, params = asyncpgsa.compile_query(query)

        try:
            res = await conn.execute(query, *params)
        except PostgresError:
            raise exceptions.DatabaseError

        return res


class SnowflakeNode(Node):
    """Node with a Snowflake ID."""

    SNOWFLAKE_TYPE: str
    """Snowflake ID type, that will be saved to the database."""

    id = SnowflakeType(default=lambda: snowflake_generator.generate(),
                       nullable=False)
    """Snowflake ID."""

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.KEYS = ((cls.id, cls.SCHEMA.c.id), )

    @classmethod
    async def list(cls, conn: Connection=None, query=None):
        query = query.order_by(cls.SCHEMA.c.id.desc())
        return await super().list(conn=conn, query=query)

    @helpers.provide_connection
    async def save(self, conn: Connection, **kwargs):
        if not self.META.saved:
            async with conn.transaction():
                snowflake = Snowflake(id=self.id, type=self.SNOWFLAKE_TYPE)
                await snowflake.save(conn=conn)
                return await super().save(conn=conn, **kwargs)
        else:
            return await super().save(conn=conn, **kwargs)


class Snowflake(SnowflakeNode):
    """Snowflake ID model and DB representation."""

    SCHEMA = schema.snowflakes
    SNOWFLAKE_TYPE = "id"

    # id = Snowflake(...)
    type = String(max_length=32, nullable=False)

    async def save(self, *args, **kwargs):
        await super(SnowflakeNode, self).save(*args, **kwargs)
