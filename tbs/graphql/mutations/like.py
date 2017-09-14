"""
The Bestory Project
"""

import logging

import graphene

from tbs import models
from tbs.graphql.queries.like import Like
from tbs.lib import exceptions
from tbs.lib import session
from tbs.lib.graphql import scalars


# class SubmitLikeAuthorInput(graphene.InputObjectType):
#     id = scalars.Snowflake(default_value=0)
#     username = graphene.String(default_value="None")


# class SubmitLikeTopicInput(graphene.InputObjectType):
#     id = scalars.Snowflake(default_value=0)
#     slug = graphene.String(default_value="unsorted")  # Constant!


class SubmitLikeInput(graphene.InputObjectType):
    # author = graphene.InputField(SubmitLikeAuthorInput)
    # topic = graphene.InputField(SubmitLikeTopicInput)
    object_id = scalars.Snowflake(required=True)


class SubmitLikePayload(graphene.Mutation):
    class Arguments:
        input = graphene.Argument(SubmitLikeInput, required=True)

    like = graphene.Field(Like)

    @staticmethod
    @session.login_required
    async def mutate(root, info, input):
        submitter = info.context["request"]["session"]["viewer"]

        try:
            like = await models.Reaction.get(user_id=submitter.id,
                                             object_id=input.object_id,
                                             reaction_id=0)
            
            if not like.is_removed:
                return SubmitLikePayload(like=Like(from_model=like))
        except exceptions.DatabaseError:
            pass

        like = models.Reaction(user_id=submitter.id, 
                               object_id=input.object_id,
                               reaction_id=0)

        try:
            await like.save()
        except exceptions.NotSavedError:
            raise exceptions.TheBestoryError("Error during like submition")

        return SubmitLikePayload(like=Like(from_model=like))
