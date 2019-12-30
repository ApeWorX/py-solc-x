import numbers
from collections import abc


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_bytes(value):
    return isinstance(value, (bytes, bytearray))


def is_text(value):
    return isinstance(value, str)


def is_string(value):
    return isinstance(value, (bytes, str, bytearray))


def is_boolean(value):
    return isinstance(value, bool)


def is_dict(obj):
    return isinstance(obj, abc.Mapping)


def is_list_like(obj):
    return not is_string(obj) and isinstance(obj, abc.Sequence)


def is_null(obj):
    return obj is None


def is_number(obj):
    return isinstance(obj, numbers.Number)
