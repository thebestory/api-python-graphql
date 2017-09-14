"""
The Bestory Project
"""

import graphene

from tbs.graphql.mutations.login import LoginPayload
from tbs.graphql.mutations.signup import SignUpPayload
from tbs.graphql.mutations.story import SubmitStoryPayload
from tbs.graphql.mutations.like import SubmitLikePayload
from tbs.lib.graphql import base
from tbs.lib.graphql import scalars


class Mutation(graphene.ObjectType):
    login = LoginPayload.Field()
    sign_up = SignUpPayload.Field()
    submit_story = SubmitStoryPayload.Field()
    submit_like = SubmitLikePayload.Field()
