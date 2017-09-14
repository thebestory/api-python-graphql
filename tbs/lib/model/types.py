"""
The Bestory Project
"""

import re
from datetime import datetime
from typing import Optional, Type, Union

from tbs.lib.model import base


__all__ = [
    "Relation",
    "Boolean",
    "Integer",
    "Float",
    "Complex",
    "String",
    "Email",
    "Bytes",
    "DateTime",
    "List",
    "Tuple",
    "Set",
    "Dictionary",
]


class Relation(base.Field):
    """Relation field for `Model`."""
    def __init__(self,
                 relation: Type[base.Model],
                 default: Optional[base.Model]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.relation = relation

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), self.relation)):
            raise TypeError


class Snowflake(base.Field):
    """Snowflake ID field."""
    def __init__(self,
                 default: Optional[int]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        if not isinstance(value, (type(None), int)):
            raise TypeError("Expected `int`")
        super().validate(instance, value)


class Boolean(base.Field):
    """Boolean field, that represents the standard Python `bool`."""
    def __init__(self,
                 default: Optional[bool]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), bool)):
            raise TypeError("Expected `bool`")


class Integer(base.Field):
    """Integer field, that represents the standard Python `int`."""
    def __init__(self,
                 minimum: Optional[int]=None,
                 maximum: Optional[int]=None,
                 default: Optional[int]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, instance, value):
        super().validate(instance, value)

        if not isinstance(value, (type(None), int)):
            raise TypeError("Expected `int`")

        if self.minimum and value < self.minimum:
            raise ValueError("Value is less, than allowed")
        if self.maximum and value > self.maximum:
            raise ValueError("Value is greater, than allowed")


class Float(base.Field):
    """Float field, that represents the standard Python `float`."""
    def __init__(self,
                 minimum: Optional[float]=None,
                 maximum: Optional[float]=None,
                 default: Optional[float]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, instance, value):
        super().validate(instance, value)

        if not isinstance(value, (type(None), float)):
            raise TypeError("Expected `float`")

        if self.minimum and value < self.minimum:
            raise ValueError("Value is less, than allowed")
        if self.maximum and value > self.maximum:
            raise ValueError("Value is greater, than allowed")


class Complex(base.Field):
    """Complex field, that represents the standard Python `complex`."""
    def __init__(self,
                 default: Optional[complex]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), complex)):
            raise TypeError("Expected `complex`")


class String(base.Field):
    """String field, that represents the standard Python `str`."""
    def __init__(self,
                 min_length: Optional[int]=None,
                 max_length: Optional[int]=None,
                 default: Optional[str]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, instance, value):
        super().validate(instance, value)

        if not isinstance(value, (type(None), str)):
            raise TypeError("Expected `str`")

        if self.min_length and len(value) < self.min_length:
            raise ValueError("Length of value is less, than allowed")
        if self.max_length and len(value) > self.max_length:
            raise ValueError("Length of value is greater, than allowed")


class Email(String):
    """Email field."""
    regex = re.compile(r".+\@.+\..+")

    def validate(self, instance, value):
        super().validate(instance, value)

        if value is not None:
            if not re.match(value):
                raise ValueError("Email is not valid")


class Bytes(base.Field):
    """Bytes field, that represents the standard Python `bytes`."""
    def __init__(self,
                 min_length: Optional[int]=None,
                 max_length: Optional[int]=None,
                 default: Optional[bytes]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, instance, value):
        super().validate(instance, value)

        if not isinstance(value, (type(None), bytes)):
            raise TypeError("Expected `bytes`")

        if self.min_length and len(value) < self.min_length:
            raise ValueError("Length of value is less, than allowed")
        if self.max_length and len(value) > self.max_length:
            raise ValueError("Length of value is greater, than allowed")


class DateTime(base.Field):
    """DateTime field, that represents the standard Python 
    `datetime.datetime`."""
    def __init__(self,
                 require_timezone: bool=False,
                 default: Optional[datetime]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)
        self.require_timezone = require_timezone

    def validate(self, instance, value):
        super().validate(instance, value)

        if not isinstance(value, (type(None), datetime)):
            raise TypeError("Expected `datetime.datetime`")

        if self.require_timezone and value.tzinfo is None:
            raise ValueError("Naive datetime is disallowed")


class List(base.Field):
    """List field, that represents the standard Python `list`."""
    def __init__(self,
                 default: Optional[list]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), list)):
            raise TypeError("Expected `list`")


class Tuple(base.Field):
    """Tuple field, that represents the standard Python `tuple`."""
    def __init__(self,
                 default: Optional[tuple]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), tuple)):
            raise TypeError("Expected `tuple`")


class Set(base.Field):
    """Set field, that represents the standard Python `set`."""
    def __init__(self,
                 default: Optional[set]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), set)):
            raise TypeError("Expected `set`")


class Dictionary(base.Field):
    """Dictionary field, that represents the standard Python `dict`."""
    def __init__(self,
                 default: Optional[dict]=None,
                 nullable: bool=True):
        super().__init__(default=default, nullable=nullable)

    def validate(self, instance, value):
        super().validate(instance, value)
        if not isinstance(value, (type(None), dict)):
            raise TypeError("Expected `dict`")
