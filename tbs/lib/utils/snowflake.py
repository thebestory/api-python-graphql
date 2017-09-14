"""
The Bestory Project
"""

from tbs.config import snowflake as config


def timestamp_of_snowflake(snowflake: int) -> int:
    """Get timestamp in ms from config epoch from Snowflake ID."""
    return snowflake >> config.TIMESTAMP_SHIFT


def real_timestamp_of_snowflake(snowflake: int) -> int:
    """Get timestamp in ms from computer epoch - 01.01.1970."""
    return timestamp_of_snowflake(snowflake) + config.EPOCH


def machine_id_of_snowflake(snowflake: int) -> int:
    """Get Machine ID from Snowflake ID."""
    return (snowflake & config.MACHINE_ID_MASK) >> config.MACHINE_ID_SHIFT


def sequence_number_of_snowflake(snowflake: int) -> int:
    """Get Sequence Number from Snowflake ID."""
    return snowflake & config.SEQUENCE_NUMBER_MASK


def first_snowflake_for_timestamp(timestamp: int, 
                                  machine_id=0) -> int:
    """First Snowflake ID for timestamp."""
    return (
        ((timestamp - config.EPOCH) << config.TIMESTAMP_SHIFT) |
        (machine_id << config.MACHINE_ID_SHIFT) |
        0
    )
