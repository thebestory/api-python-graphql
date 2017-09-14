"""
The Bestory Project
"""

import graphene

from tbs.graphql.queries.user import User
from tbs.lib import exceptions
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


class JWT(graphene.ObjectType):
    value = graphene.String()

    iss = graphene.String()
    # aud = graphene.String()
    iat = graphene.Int()
    nbf = graphene.Int()
    exp = graphene.Int()


class Session(graphene.ObjectType, interfaces=[base.Node]):
    user = graphene.Field(User)
    jwt = graphene.Field(JWT)
