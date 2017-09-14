"""
The Bestory Project
"""

import graphene

from tbs import models
from tbs.graphql.queries.user import User
from tbs.lib import exceptions


class SignUpInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)


class SignUpPayload(graphene.Mutation):
    class Arguments:
        input = graphene.Argument(SignUpInput, required=True)

    user = graphene.Field(User)

    @staticmethod
    async def mutate(root, info, input):
        try:
            user = await models.User.get_by_username(input.username)
            raise exceptions.TheBestoryError("Username already taken")
        except exceptions.NotFoundError:
            pass

        user = models.User(username=input.username, password=input.password)

        try:
            await user.save()    
        except exceptions.NotSavedError:
            raise exceptions.TheBestoryError("Error during registration")

        return SignUpPayload(user=User(from_model=user))
