"""
The Bestory Project
"""

from functools import partial

import graphene

from tbs import models
from tbs.graphql.queries.comment import (
    Comment,
    CommentListing,
    CommentHolder,
)
from tbs.graphql.queries.like import (
    Like,
    LikeListing,
    LikeHolder,
)
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


class User(graphene.ObjectType, interfaces=[base.Node, StoryHolder,
                                            CommentHolder, LikeHolder]):
    """A user is an individual's account on The Bestory."""
    username = graphene.String()
    registered_at = scalars.DateTime()
    story_likes_count = graphene.Int()
    comment_likes_count = graphene.Int()

    stories = partial(StoryListing, resolver=None)()
    comments = partial(CommentListing, resolver=None)()
    likes = partial(LikeListing, resolver=None)()

    def __init__(self, from_model, *args, **kwargs):
        """Convert User model instance to the GraphQL User type
        instance."""
        super().__init__(*args, **kwargs, 
                         id=from_model.id,
                         username=from_model.username,
                         stories_count=from_model.stories_count,
                         comments_count=from_model.comments_count,
                         story_likes_count=from_model.story_reactions_count,
                         comment_likes_count=from_model.comment_reactions_count,
                         registered_at=from_model.registered_at)
        self.source_model = from_model

    def resolve_likes_count(self, info):
        return self.story_likes_count + self.comment_likes_count

    async def resolve_stories(self, info, *args, **kwargs):
        kwargs["authors"] = [self.id]
        return await Story.list(self, info, *args, **kwargs)

    async def resolve_comments(self, info, *args, **kwargs):
        kwargs["authors"] = [self.id]
        return await Comment.list(self, info, *args, **kwargs)

    async def resolve_likes(self, info, *args, **kwargs):
        return await Like.list(self, info, *args, **kwargs, user=self)

    @classmethod
    async def get(cls, root, info, id=None, username=None):
        try:
            if id is not None:
                user = await models.User.get(id=id)
            elif username is not None:
                user = await models.User.get_by_username(username)
            else:
                raise ValueError("Provide `id` or `username`")

            return cls(from_model=user)
        except exceptions.DatabaseError:
            raise ValueError("User not found")

    @classmethod
    async def list(cls, root, info, before=None, after=None, limit=None):
        pivot, direction, limit = listing_validator.validate(before, after,
                                                             limit)
        users = await models.User.list()

        if pivot is not None:
            counter = 0

            for user in users:
                counter += 1
                if user.id == pivot:
                    if direction == listing.Direction.BEFORE:
                        return [cls(from_model=user) for user in users[max(0, counter - limit - 1):counter - 1]]
                    elif direction == listing.Direction.AFTER:
                        return [cls(from_model=user) for user in users[counter:min(len(users), counter + limit)]]
                    else:
                        pass  # AROUND direction is not supported

            raise ValueError("Pivot user not found")

        return [cls(from_model=user) for user in users[:min(len(users), limit)]]


UserField = partial(graphene.Field, User, id=scalars.Snowflake(),
                    username=graphene.String(), resolver=User.get)

UserListing = partial(base.Listing, User,
                      limit=graphene.Int(
                          default_value=listing_validator.default_limit),
                      resolver=User.list)
