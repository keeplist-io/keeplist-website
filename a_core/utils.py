import re

type_id_regex = re.compile(r"^[a-zA-Z0-9]+_[a-zA-Z0-9]{26}$")
encoded_regex = re.compile(r"^[a-zA-Z0-9]{26}$")

uuid_v7_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")

def is_valid_encoded(typeid: str) -> bool:
    """Check if a given string is a valid encoded UUID."""
    return encoded_regex.match(typeid) is not None


def is_valid_typeid(typeid: str) -> bool:
    """Check if a given string is a valid TypeID or UUID."""
    return type_id_regex.match(typeid) is not None


def is_valid_uuid(typeid: str) -> bool:
    """Check if a given string is a valid UUID."""
    return uuid_v7_pattern.match(typeid) is not None


def is_valid(typeid: str, allow_type_less: bool = False) -> bool:
    """Check if a given string is a valid TypeID or UUID."""
    if allow_type_less:
        return is_valid_encoded(typeid) or is_valid_uuid(typeid) or is_valid_typeid(typeid)
    return is_valid_typeid(typeid) or is_valid_uuid(typeid)
