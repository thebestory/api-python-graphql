"""
The Bestory Project
"""

from functools import partial

import graphene

from tbs import models
from tbs.graphql.queries.story import (
    Story,
    StoryListing,
    StoryHolder,
)
from tbs.lib import exceptions
from tbs.lib import listing
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


listing_validator = listing.Listing(min_limit=1, 
                                    max_limit=100, 
                                    default_limit=25)


class Topic(graphene.ObjectType, interfaces=[base.Node, StoryHolder]):
    """Topic allows to divide the content according to their
    meaning."""
    source_model = None

    title = graphene.String()
    slug = graphene.String()
    description = graphene.String()
    is_active = graphene.Boolean()

    stories = partial(StoryListing, resolver=None)()

    def __init__(self, from_model, *args, **kwargs):
        """Convert Topic model instance to the GraphQL Topic type
        instance."""
        super().__init__(*args, **kwargs, 
                         id=from_model.id,
                         title=from_model.title,
                         slug=from_model.slug,
                         description=from_model.description,
                         stories_count=from_model.stories_count,
                         is_active=from_model.is_active)
        self.source_model = from_model

    async def resolve_stories(self, info, *args, **kwargs):
        kwargs["topics"] = [self.id]
        return await Story.list(self, info, *args, **kwargs)

    @classmethod
    async def get(cls, root, info, id=None, slug=None):
        try:
            if id is not None:
                topic = await models.Topic.get(id=id)
            elif slug is not None:
                topic = await models.Topic.get_by_slug(slug)
            else:
                raise ValueError("Provide `id` or `slug`")

            return cls(from_model=topic)
        except exceptions.DatabaseError:
            raise ValueError("Topic not found")

    @classmethod
    async def list(cls, root, info, before=None, after=None, limit=None):
        pivot, direction, limit = listing_validator.validate(before, after,
                                                             limit)
        topics = await models.Topic.list(is_active=True)

        if pivot is not None:
            counter = 0

            for topic in topics:
                counter += 1
                if topic.id == pivot:
                    if direction == listing.Direction.BEFORE:
                        return [cls(from_model=topic) for topic in topics[max(0, counter - limit - 1):counter - 1]]
                    elif direction == listing.Direction.AFTER:
                        return [cls(from_model=topic) for topic in topics[counter:min(len(topics), counter + limit)]]
                    else:
                        pass  # AROUND direction is not supported

            raise ValueError("Pivot topic not found")

        return [cls(from_model=topic) for topic in topics[:min(len(topics), limit)]]


TopicField = partial(graphene.Field, Topic, id=scalars.Snowflake(),
                     slug=graphene.String(), resolver=Topic.get)

TopicListing = partial(base.Listing, Topic,
                       limit=graphene.Int(
                           default_value=listing_validator.default_limit),
                       resolver=Topic.list)
