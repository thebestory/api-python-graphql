"""
The Bestory Project
"""

import graphene

from tbs.graphql.query import Query
from tbs.graphql.mutation import Mutation


schema = graphene.Schema(query=Query, mutation=Mutation)
"""GraphQL schema definition."""
