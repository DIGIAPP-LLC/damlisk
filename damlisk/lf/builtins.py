from enum import Enum


def lf_name(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Enum):
        return value.name
    return str(value)
