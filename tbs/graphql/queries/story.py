"""
The Bestory Project
"""

from functools import partial

import graphene

from tbs import models
from tbs.lib import exceptions
from tbs.lib import listing
from tbs.graphql.queries.comment import (
    Comment,
    CommentListing,
    Commentable,
    CommentHolder,
)
from tbs.graphql.queries.like import (
    Like,
    LikeListing,
    Likeable,
    LikeHolder,
)
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


listing_validator = listing.Listing(min_limit=1, 
                                    max_limit=100, 
                                    default_limit=25)


class StoryListingSection(graphene.Enum):
    LATEST = 0
    TOP = 1
    HOT = 2
    RANDOM = 3


class Story(graphene.ObjectType, interfaces=[base.Node, Commentable,
                                             CommentHolder, Likeable,
                                             LikeHolder]):
    source_model = None

    """Stories is a main content of The Bestory."""
    author = graphene.Field("tbs.graphql.queries.user.User")
    topic = graphene.Field("tbs.graphql.queries.topic.Topic")
    content = graphene.String()
    is_liked_by_viewer = graphene.Boolean()
    is_published = graphene.Boolean()
    is_removed = graphene.Boolean()
    submitted_at = scalars.DateTime()
    published_at = scalars.DateTime()
    edited_at = scalars.DateTime()

    comments = partial(CommentListing, resolver=None)()
    likes = partial(LikeListing, resolver=None)()

    def __init__(self, from_model, *args, **kwargs):
        """Convert Story model instance to the GraphQL Story type
        instance."""
        super().__init__(*args, **kwargs, 
                         id=from_model.id,
                         author=from_model.author_id,
                         topic=from_model.topic_id,
                         content=from_model.content,
                         comments_count=from_model.comments_count,
                         likes_count=from_model.reactions_count,
                         is_published=from_model.is_published,
                         is_removed=from_model.is_removed,
                         submitted_at=from_model.submitted_at,
                         published_at=from_model.published_at,
                         edited_at=from_model.edited_at)
        self.source_model = from_model

    async def resolve_author(self, info):
        from tbs.graphql.queries.user import User

        user = await self.source_model.author
        return User(from_model=user)

    async def resolve_topic(self, info):
        from tbs.graphql.queries.topic import Topic

        topic = await self.source_model.topic
        return Topic(from_model=topic)

    async def resolve_comments(self, info, *args, **kwargs):
        kwargs["stories"] = [self.id]
        return await Comment.list(self, info, *args, **kwargs)

    async def resolve_likes(self, info, *args, **kwargs):
        return await Like.list(self, info, *args, **kwargs, object=self)

    async def resolve_is_liked_by_viewer(self, info):
        viewer = info.context["request"]["session"]["viewer"]

        if viewer is not None:
            try:
                like = await models.Reaction.get(user_id=viewer.id,
                                                 object_id=self.id,
                                                 reaction_id=0)
                return not like.is_removed
            except exceptions.DatabaseError:
                return False

        return False

    @classmethod
    async def get(cls, root, info, id):
        try:
            story = await models.Story.get(id=id)
            return cls(from_model=story)
        except exceptions.DatabaseError:
            raise ValueError("Story not found")

    @classmethod
    async def list(cls, root, info, authors=[], topics=[],
                   section=StoryListingSection.LATEST,
                   before=None, after=None, limit=None):
        pivot, direction, limit = listing_validator.validate(before, after,
                                                             limit)
        if section == StoryListingSection.LATEST:
            list_method = models.Story.list_latest
        elif section == StoryListingSection.TOP:
            list_method = models.Story.list_top
        elif section == StoryListingSection.HOT:
            list_method = models.Story.list_hot
        elif section == StoryListingSection.RANDOM:
            list_method = models.Story.list_random
        else:
            list_method = models.Story.list_latest

        stories = partial(list_method)

        if authors is not None:
            stories = partial(stories, authors=authors)
        if topics is not None:
            stories = partial(stories, topics=topics)

        stories = await stories()

        if pivot is not None:
            counter = 0

            for story in stories:
                counter += 1
                if story.id == pivot:
                    if direction == listing.Direction.BEFORE:
                        return [cls(from_model=story) for story in stories[max(0, counter - limit - 1):counter - 1]]
                    elif direction == listing.Direction.AFTER:
                        return [cls(from_model=story) for story in stories[counter:min(len(stories), counter + limit)]]
                    else:
                        pass  # AROUND direction is not supported

            raise ValueError("Pivot story not found")

        return [cls(from_model=story) for story in stories[:min(len(stories), limit)]]


StoryField = partial(graphene.Field, Story,
                     id=scalars.Snowflake(required=True),
                     resolver=Story.get)

StoryListing = partial(base.Listing, Story,
                       limit=graphene.Int(
                           default_value=listing_validator.default_limit),
                       authors=graphene.List(scalars.Snowflake, default_value=[]),
                       topics=graphene.List(scalars.Snowflake, default_value=[]),
                       section=StoryListingSection(
                           default_value=StoryListingSection.LATEST),
                       resolver=Story.list)


class StoryHolder(graphene.Interface):
    """Interface for types, that contains stories."""
    stories = StoryListing()
    stories_count = graphene.Int()
