"""
The Bestory Project
"""

from functools import partial

import graphene

from tbs import models
from tbs.lib import exceptions
from tbs.lib import listing
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


class CommentListingSection(graphene.Enum):
    LATEST = 0
    TOP = 1


class Comment(graphene.ObjectType, interfaces=[base.Node, Likeable, LikeHolder]):
    """Users can post a comments to the stories, expressing their 
    feelings and opinions."""
    source_model = None

    author = graphene.Field("tbs.graphql.queries.user.User")
    story = graphene.Field("tbs.graphql.queries.story.Story")
    content = graphene.String()
    is_liked_by_viewer = graphene.Boolean()
    is_removed = graphene.Boolean()
    submitted_at = scalars.DateTime()
    edited_at = scalars.DateTime()

    likes = partial(LikeListing, resolver=None)()

    def __init__(self, from_model, *args, **kwargs):
        """Convert Comment model instance to the GraphQL Comment type
        instance."""
        super().__init__(*args, **kwargs, 
                         id=from_model.id,
                         author=from_model.author_id,
                         story=from_model.story_id,
                         content=from_model.content,
                         likes_count=from_model.reactions_count,
                         is_removed=from_model.is_removed,
                         submitted_at=from_model.submitted_at,
                         edited_at=from_model.edited_at)
        self.source_model = from_model

    async def resolve_author(self, info):
        from tbs.graphql.queries.user import User

        user = await self.source_model.author
        return User(from_model=user)

    async def resolve_story(self, info):
        from tbs.graphql.queries.story import Story

        story = await self.source_model.story
        return Story(from_model=story)

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
            comment = await models.Comment.get(id=id)
            return cls(from_model=comment)
        except exceptions.DatabaseError:
            raise ValueError("Comment not found")

    @classmethod
    async def list(cls, root, info, authors=[], stories=[],
                   section=CommentListingSection.LATEST,
                   before=None, after=None, limit=None):
        pivot, direction, limit = listing_validator.validate(before, after,
                                                             limit)
        if section == CommentListingSection.LATEST:
            list_method = models.Comment.list_latest
        elif section == CommentListingSection.TOP:
            list_method = models.Comment.list_top
        else:
            list_method = models.Comment.list_latest

        comments = partial(list_method)

        if authors is not None:
            comments = partial(comments, authors=authors)
        if stories is not None:
            comments = partial(comments, stories=stories)

        comments = await comments()

        if pivot is not None:
            counter = 0

            for comment in comments:
                counter += 1
                if comment.id == pivot:
                    if direction == listing.Direction.BEFORE:
                        return [cls(from_model=comment) for comment in comments[max(0, counter - limit - 1):counter - 1]]
                    elif direction == listing.Direction.AFTER:
                        return [cls(from_model=comment) for comment in comments[counter:min(len(comments), counter + limit)]]
                    else:
                        pass  # AROUND direction is not supported

            raise ValueError("Pivot comment not found")

        return [cls(from_model=comment) for comment in comments[:min(len(comments), limit)]]


CommentField = partial(graphene.Field, Comment,
                       id=scalars.Snowflake(required=True),
                       resolver=Comment.get)

CommentListing = partial(base.Listing, Comment,
                         limit=graphene.Int(
                             default_value=listing_validator.default_limit),
                         authors=graphene.List(scalars.Snowflake, default_value=[]),
                         stories=graphene.List(scalars.Snowflake, default_value=[]),
                         section=CommentListingSection(
                             default_value=CommentListingSection.LATEST),
                         resolver=Comment.list)


class Commentable(base.Node):
    """Represents an object, that can be commented by the user."""
    pass


class CommentHolder(graphene.Interface):
    """Interface for types, that contains comments."""
    comments = CommentListing()
    comments_count = graphene.Int()
