"""
The Bestory Project
"""

import logging
import time
import typing

from tbs.config import snowflake as config


logger = logging.getLogger(__name__)


def __generator(sleep=lambda x: time.sleep(x / 1000.0),
                now=lambda: int(time.time() * 1000)):
    """Snowflake ID generator.
    
    Snowflake ID is a 63 bit integer, that can be used as a global
    unique ID.
    Generator parameters can be changed.
    Generator contains a set of helper methods for working with
    Snowflake IDs. These methods use the generator parameters.

    TODO: Async sleep.
    TODO: Snowflake ID generation server.
    """
    last_timestamp = -1
    sequence_number = 0

    while True:
        timestamp = now()

        if last_timestamp > timestamp:
            logger.warning(
                "Clock is moving backwards. Waiting until %i" % last_timestamp)
            sleep(last_timestamp - timestamp)
            continue

        if last_timestamp == timestamp:
            sequence_number = (sequence_number + 1) & config.SEQUENCE_NUMBER_MASK
            if sequence_number == 0:
                logger.warning("Sequence overflow")
                sequence_number = -1 & config.SEQUENCE_NUMBER_MASK
                sleep(1)
                continue
        else:
            sequence_number = 0

        last_timestamp = timestamp

        yield (
            ((timestamp - config.EPOCH) << config.TIMESTAMP_SHIFT) |
            (config.MACHINE_ID << config.MACHINE_ID_SHIFT) |
            sequence_number
        )


snowflake_generator = __generator()
"""Snowflake ID generator."""


def generate() -> int:
    """Generate a new Snowflake ID."""
    return next(snowflake_generator)
