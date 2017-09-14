"""
The Bestory Project
"""

import graphene

from tbs.graphql.queries.comment import (
    Comment,
    CommentField,
    CommentListing,
)
from tbs.graphql.queries.story import (
    Story,
    StoryField,
    StoryListing,
)
from tbs.graphql.queries.topic import (
    Topic,
    TopicField,
    TopicListing,
)
from tbs.graphql.queries.user import (
    User,
    UserField, 
    UserListing,
)
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


class Query(graphene.ObjectType):
    user = UserField()
    users = UserListing()

    topic = TopicField()
    topics = TopicListing()

    story = StoryField()
    stories = StoryListing()

    comment = CommentField()
    comments = CommentListing()
