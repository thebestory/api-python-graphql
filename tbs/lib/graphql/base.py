"""
The Bestory Project
"""

import graphene

from tbs.lib.graphql import scalars


class Node(graphene.Interface):
    """Represents an object."""
    id = scalars.Snowflake(required=True)


class Listing(graphene.List):
    """Listing provides an easy way to iterate through the 
    collection."""
    def __init__(self, *args, **kwargs):
        kwargs["before"] = scalars.Snowflake()
        kwargs["after"] = scalars.Snowflake()
        kwargs["limit"] = graphene.Int()
        super().__init__(*args, **kwargs)
