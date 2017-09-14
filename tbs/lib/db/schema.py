"""
The Bestory Project
"""

import sqlalchemy as sa

from tbs.lib.db.table import Table
from tbs.lib.db.types import DateTime


metadata = sa.MetaData()
"""SQLAlchemy Metadata instance."""


snowflakes = Table(
    "snowflakes",
    metadata,

    sa.Column("id", sa.BigInteger),
    sa.Column("type", sa.String))

users = Table(
    "users",
    metadata,

    sa.Column("id", sa.BigInteger),

    sa.Column("username", sa.String),
    sa.Column("password", sa.String),

    sa.Column("posts_count", sa.Integer),
    sa.Column("likes_count", sa.Integer),

    sa.Column("registered_at", DateTime))

topics = Table(
    "topics",
    metadata,

    sa.Column("id", sa.BigInteger),

    sa.Column("title", sa.String),
    sa.Column("slug", sa.String),

    sa.Column("description", sa.Text),

    sa.Column("posts_count", sa.Integer),

    sa.Column("is_active", sa.Boolean))

posts = Table(
    "posts",
    metadata,

    sa.Column("id", sa.BigInteger),

    sa.Column("author_id", sa.BigInteger),
    sa.Column("parent_id", sa.BigInteger),

    sa.Column("content", sa.Text),

    sa.Column("responses_count", sa.Integer),
    sa.Column("likes_count", sa.Integer),

    sa.Column("is_published", sa.Boolean),
    sa.Column("is_removed", sa.Boolean),

    sa.Column("submitted_at", DateTime),
    sa.Column("published_at", DateTime),
    sa.Column("edited_at", DateTime))

posts_topics = Table(
    "posts_topics",
    metadata,

    sa.Column("post_id", sa.BigInteger),
    sa.Column("topic_id", sa.BigInteger))

likes = Table(
    "likes",
    metadata,

    sa.Column("user_id", sa.BigInteger),
    sa.Column("object_id", sa.BigInteger),

    sa.Column("submitted_at", DateTime))
