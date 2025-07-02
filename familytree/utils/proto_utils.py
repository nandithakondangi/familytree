import logging

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message

# Assuming proto files are compiled and accessible as in proto_handler.py
# This implies that the directory containing the 'proto' package is in PYTHONPATH.
import familytree.proto.utils_pb2 as utils_pb2

# Get a logger instance for this module
logger = logging.getLogger(__name__)


def get_month_name(month_enum_value: int) -> str:
    """Returns the string name of a TamilMonth enum value."""
    return utils_pb2.TamilMonth.Name(month_enum_value)


def get_star_name(star_enum_value: int) -> str:
    """Returns the string name of a TamilStar enum value."""
    return utils_pb2.TamilStar.Name(star_enum_value)


def get_gender_name(gender_enum_value: int) -> str:
    """Returns the string name of a Gender enum value."""
    return utils_pb2.Gender.Name(gender_enum_value)


def get_paksham_name(paksham_enum_value: int) -> str:
    """Returns the string name of a Paksham enum value."""
    return utils_pb2.Paksham.Name(paksham_enum_value)


def get_thithi_name(thithi_enum_value: int) -> str:
    """Returns the string name of a Thithi enum value."""
    return utils_pb2.Thithi.Name(thithi_enum_value)


def get_enum_values_from_proto_schema(
    enum_name: str, proto_module=utils_pb2
) -> list[str]:
    """Retrieves the valid string names for a given enum from the protobuf schema."""
    try:
        enum_descriptor = proto_module.DESCRIPTOR.enum_types_by_name.get(enum_name)
        if enum_descriptor:
            return [value.name for value in enum_descriptor.values]
        logger.error(f"Enum '{enum_name}' not found in {proto_module.__name__}.")
        return []
    except AttributeError as e:
        logger.error(f"Error accessing descriptor for enum '{enum_name}': {e}")
        return []
    except Exception as e:
        logger.exception(
            f"An unexpected error occurred getting enum values for '{enum_name}': {e}"
        )
        return []


def apply_changes(a: Message, b: Message):
    """
    Recursively applies set fields from message 'b' to message 'a'.

    - For singular fields (including enums), it overwrites the value.
    - For 'oneof' fields, it correctly sets the new field, clearing the old one.
    - For 'map' fields, it clears the map in 'a' and copies all entries from 'b'.
    - For repeated fields, it clears the list in 'a' and adds all elements from 'b'.
    - For nested messages, it recursively applies changes.
    """
    if a.DESCRIPTOR.full_name != b.DESCRIPTOR.full_name:
        raise TypeError("Messages 'a' and 'b' must be of the same type.")

    for field_descriptor, field_value in b.ListFields():
        # Check if the field is a map
        is_map = (
            field_descriptor.type == FieldDescriptor.TYPE_MESSAGE
            and field_descriptor.message_type.GetOptions().map_entry
        )

        if is_map:
            # Handle map fields: clear destination and update from source
            map_a = getattr(a, field_descriptor.name)
            map_a.update(field_value)
        elif field_descriptor.label == FieldDescriptor.LABEL_REPEATED:
            # Handle repeated fields (lists): clear and extend
            list_a = getattr(a, field_descriptor.name)
            set_a = set(list_a)
            set_b = set(field_value)
            del list_a[:]
            list_a.extend(sorted(list(set_a.union(set_b))))
        elif field_descriptor.type == FieldDescriptor.TYPE_MESSAGE:
            # Handle nested messages: recurse
            nested_a = getattr(a, field_descriptor.name)
            # Note: We pass field_value directly, which is the nested message from 'b'
            apply_changes(nested_a, field_value)
        else:
            # Handle singular fields (including those in a 'oneof' and enums)
            setattr(a, field_descriptor.name, field_value)
