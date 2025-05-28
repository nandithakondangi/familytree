import logging

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
