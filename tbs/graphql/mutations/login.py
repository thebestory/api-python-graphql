"""
The Bestory Project
"""

import graphene

from tbs import models
from tbs import snowflake_generator
from tbs.graphql.queries.user import User
from tbs.graphql.queries.session import JWT, Session
from tbs.lib import exceptions
from tbs.lib import session
from tbs.lib import utils


class LoginInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)


class LoginPayload(graphene.Mutation):
    class Arguments:
        input = graphene.Argument(LoginInput, required=True)

    session = graphene.Field(Session)

    @staticmethod
    async def mutate(root, info, input):
        try:
            user = await models.User.get_by_username(input.username)
        except exceptions.NotFoundError:
            raise exceptions.TheBestoryError("User not found")

        if utils.password.verify(input.password, user.password):
            encoded_jwt = await session.create(user)
            decoded_jwt = utils.jwt.decode(encoded_jwt, verify=False)

            return LoginPayload(
                session=Session(
                    id=snowflake_generator.generate(),
                    user=User(from_model=user),
                    jwt=JWT(
                        value=encoded_jwt,
                        iss=decoded_jwt["iss"],
                        iat=decoded_jwt["iat"],
                        nbf=decoded_jwt["nbf"],
                        exp=decoded_jwt["exp"])))
        else:
            raise exceptions.TheBestoryError("Password is incorrect")
