"""
The Bestory Project
"""

import datetime

import pendulum
import graphene
from graphql.language import ast


class Snowflake(graphene.Scalar):
    """The `Snowflake` scalar type represents a Snowflake ID.
    Snowflake ID is a 63 bit integer. Note that the Snowflake ID values
    are returned as strings."""
    @classmethod
    def serialize(cls, value):
        assert isinstance(value, (int, str))
        return str(value)

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return int(value)


class DateTime(graphene.Scalar):
    """The `DateTime` scalar type represents a DateTime
    value as specified by
    [ISO8601](https://en.wikipedia.org/wiki/ISO_8601)."""
    allowed_types = (pendulum.Date, pendulum.Pendulum,
                     datetime.date, datetime.datetime)

    @classmethod
    def serialize(cls, value):
        assert isinstance(value, cls.allowed_types)
        return value.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return pendulum.parse(value)


class Date(DateTime):
    """The `Date` scalar type represents a Date
    value as specified by
    [ISO8601](https://en.wikipedia.org/wiki/ISO_8601)."""
    allowed_types = (pendulum.Date, datetime.date)


class Time(DateTime):
    """The `Time` scalar type represents a Time
    value as specified by
    [ISO8601](https://en.wikipedia.org/wiki/ISO_8601)."""
    allowed_types = (pendulum.Time, datetime.time)
