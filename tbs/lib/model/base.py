"""
The Bestory Project
"""

import inspect


__all__ = [
    "Field",
    "Meta",
    "MetaInstance",
    "Model",
    "validator"
]


class Field:
    """Model's base field class aka data descriptor."""

    def __init__(self, default=None, nullable: bool=True):
        self.name = None
        self.nullable = nullable
        self.default = default

    def __get__(self, instance, type=None):
        if instance is None:
            return self  # return descriptor on a class
        return instance.META.get_value(self)

    def __set__(self, instance, value):
        self.validate(instance, value)
        for validator in instance.META.validators[self]:
            validator(instance, value)

        instance.META.set_value(self, value)

    def validate(self, instance, value):
        """Invoked before assigning the value to ensure the correct one
        is given. Should raises an error, if value is incorrect."""
        if value is None:
            if not self.nullable:
                raise ValueError("Null value is disallowed")


class Meta:
    """Meta object, that contains information about the model."""
    def __init__(self):
        self.fields = set()
        self.validators = {}
        self.locked = set()

    def add_field(self, field: Field):
        if not isinstance(field, Field):
            raise ValueError("Only `Field` instance can be provided")
        if field in self.fields:
            raise ValueError("Field is added yet")
        self.fields |= {field}
        self.validators[field] = set()

    def add_validator(self, field: Field, validator):
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.validators[field] |= {validator}

    def lock(self, field: Field):
        """Lock field and prevent any changes."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.locked |= {field}

    def unlock(self, field: Field):
        """Unlock field and allow changes."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.locked -= {field}
    
    def lock_all(self):
        """Lock all fields and prevent any changes."""
        self.locked = self.fields.copy()

    def unlock_all(self):
        """Unlock all fields and allow changes."""
        self.locked = set()


class MetaInstance:
    """Meta object, that contains information about the model, and
    model instance data."""
    def __init__(self, meta: Meta, obj):
        self.static = meta  # global meta
        self.obj = obj

        self.locked = set()
        self.values = {}

        # While all fields is unlocked, fill it by default values
        for field in self.static.fields:
            value = None
            try:
                value = field.default()
            except TypeError:
                value = field.default
            self.set_value(field, value)

        self.locked = self.static.locked.copy()

    @property
    def fields(self):
        return self.static.fields

    @property
    def validators(self):
        return self.static.validators

    def lock(self, field: Field):
        """Lock field and prevent any changes."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.locked |= {field}

    def unlock(self, field: Field):
        """Unlock field and allow changes."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        self.locked -= {field}

    def lock_all(self):
        """Lock all fields and prevent any changes."""
        for field in self.fields:
            self.lock(field)

    def unlock_all(self):
        """Unlock all fields and allow changes."""
        for field in self.fields:
            self.unlock(field)

    def get_value(self, field: Field):
        """Get the field value."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        return self.values[field]

    def set_value(self, field: Field, value):
        """Change the field value."""
        if field not in self.fields:
            raise AttributeError("Field not found")
        if field in self.locked:
            raise AttributeError("Field is locked")
        self.values[field] = value

    def validate(self):
        """Force check all fields values by validators."""
        for field in self.fields:
            value = self.get_value(field)
            field.validate(self.obj, value)
            for validator in self.validators[field]:
                validator(self.obj, value)


class Model:
    """
    Model class.
    """
    def __init__(self, *args, **kwargs):
        meta = self.META
        meta_instance = MetaInstance(meta, self)
        self.META = meta_instance

        for field in meta.fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        if (getattr(cls, "META", None) is not None
            and not isinstance(cls.META, Meta)):
            raise AttributeError(
                "Model cannot contains `META` property")

        meta = Meta()
        cls.META = meta

        for attr_name, attr_value in inspect.getmembers(cls):
            if isinstance(attr_value, Field):
                attr_value.name = attr_name
                meta.add_field(attr_value)
            elif isinstance(getattr(attr_value, "validator_of", None), Field):
                meta.add_validator(attr_value.validator_of, attr_value)


def validator(field: Field):
    """Decorator for register field validators."""
    if not isinstance(field, Field):
        raise ValueError("Only `Field` instance can be provided.")

    def decorator(fn):
        fn.validator_of = field
        return fn

    return decorator
