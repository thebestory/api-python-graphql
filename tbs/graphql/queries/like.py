"""
The Bestory Project
"""

from functools import partial

import graphene

from tbs import models
from tbs.lib import exceptions
from tbs.lib import listing
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


listing_validator = listing.Listing(min_limit=1, 
                                    max_limit=1000, 
                                    default_limit=100)


class Like(graphene.ObjectType):
    """Like allows to support the author of the content and raise this
    content in the rating."""
    source_model = None

    user = graphene.Field("tbs.graphql.queries.user.User")
    object = graphene.Field(lambda: Likeable)
    submitted_at = scalars.DateTime()

    def __init__(self, from_model, *args, **kwargs):
        """Convert Like model instance to the GraphQL Like type
        instance."""
        super().__init__(*args, **kwargs, 
                         user=from_model.user_id, 
                         object=from_model.object_id, 
                         submitted_at=from_model.submitted_at)
        self.source_model = from_model

    async def resolve_user(self, info):
        from tbs.graphql.queries.user import User

        user = await self.source_model.user
        return User(from_model=user)

    async def resolve_object(self, info):
        from tbs.graphql.queries.comment import Comment
        from tbs.graphql.queries.story import Story

        object = await self.source_model.object

        if isinstance(object, models.Comment):
            return Comment(from_model=object)
        elif isinstance(object, models.Story):
            return Story(from_model=object)
        else:
            return None

    @classmethod
    async def get(cls, root, info, id=None):
        return None

    @classmethod
    async def list(cls, root, info, before=None, after=None, limit=None,
                   user=None, object=None):
        if user is not None:
            likes = await models.Reaction.list(users=[user.id])
        elif object is not None:
            likes = await models.Reaction.list(objects=[object.id])
        else:
            likes = await models.Reaction.list()

        if before is not None and after is not None:
            raise ValueError("Provide only before or after")

        return [cls(from_model=like) for like in likes[:min(len(likes), limit)]]


LikeField = partial(graphene.Field, Like, id=scalars.Snowflake(),
                    resolver=Like.get)

LikeListing = partial(base.Listing, Like,
                      limit=graphene.Int(
                          default_value=listing_validator.default_limit),
                      resolver=Like.list)


class Likeable(base.Node):
    """Represents an object, that can be liked by the user."""
    pass


class LikeHolder(graphene.Interface):
    """Represents an object, that contains likes."""
    likes = LikeListing()
    likes_count = graphene.Int()
