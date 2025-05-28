import datetime
import logging

# Assuming proto files are compiled and accessible as in proto_handler.py
# This implies that the directory containing the 'proto' package is in PYTHONPATH.
import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2

# Get a logger instance for this module
logger = logging.getLogger(__name__)


def populate_gregorian_date(
    date_proto: utils_pb2.GregorianDate, input_data: dict, prefix: str
) -> tuple[bool, str | None]:
    """
    Populates and validates a GregorianDate protobuf message from input data.

    Args:
        date_proto: The GregorianDate message to populate.
        input_data: The dictionary containing potential date parts.
        prefix: The prefix for the keys in input_data (e.g., "dob", "dod").

    Returns:
        tuple[bool, str | None]: (True, None) if successful or no input.
                                 (False, error_message) if invalid data.
    """
    day_str = input_data.get(f"{prefix}_date")
    month_str = input_data.get(f"{prefix}_month")
    year_str = input_data.get(f"{prefix}_year")

    if not (day_str or month_str or year_str):  # No data provided
        return True, None

    try:
        day = int(day_str or 0)
        month = int(month_str or 0)
        year = int(year_str or 0)

        if not (day and month and year):  # Incomplete date
            return (
                False,
                f"Incomplete Gregorian date provided for '{prefix}'. Please provide day, month, and year.",
            )

        try:
            parsed_date = datetime.date(year, month, day)
        except ValueError as e:
            if "month must be in 1..12" in str(e):
                return (
                    False,
                    f"Invalid month ({month}) for '{prefix}'. Month must be between 1 and 12.",
                )
            elif "day is out of range for month" in str(e):
                return (
                    False,
                    f"Invalid day ({day}) for '{prefix}' month {month} and year {year}.",
                )
            elif "year" in str(e):  # Catch other year-related errors
                return False, f"Invalid year ({year}) provided for '{prefix}'. {e}"
            else:  # Generic fallback
                return (
                    False,
                    f"Invalid Gregorian date for '{prefix}': Day={day}, Month={month}, Year={year}. Reason: {e}",
                )

        if parsed_date > datetime.date.today():
            return (
                False,
                f"Gregorian date for '{prefix}' ({parsed_date.strftime('%Y-%m-%d')}) cannot be in the future.",
            )

        if year < 1000:  # Sensible minimum year
            return (
                False,
                f"Year ({year}) for '{prefix}' seems too far in the past. Please check.",
            )

        date_proto.date = day
        date_proto.month = month
        date_proto.year = year
        return True, None

    except (ValueError, TypeError):  # Non-numeric input
        return (
            False,
            f"Non-numeric value encountered for '{prefix}' date parts (Day='{day_str}', Month='{month_str}', Year='{year_str}'). Please enter numbers.",
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error validating/populating Gregorian date for prefix '{prefix}': {e}"
        )
        return (
            False,
            f"An unexpected error occurred processing the Gregorian date for '{prefix}'.",
        )


def populate_traditional_date(
    trad_date_proto: utils_pb2.TraditionalDate,
    input_data: dict,
    prefix: str,
    month_enum,  # e.g., utils_pb2.TamilMonth
    star_enum=None,
    paksham_enum=None,
    thithi_enum=None,
) -> tuple[bool, str | None]:
    """
    Populates and validates a TraditionalDate protobuf message from input data.

    Args:
        trad_date_proto: The TraditionalDate message to populate.
        input_data: The dictionary containing potential date parts.
        prefix: The prefix for the keys in input_data.
        month_enum: The protobuf enum type for the month.
        star_enum: Optional protobuf enum type for the star.
        paksham_enum: Optional protobuf enum type for Paksham.
        thithi_enum: Optional protobuf enum type for Thithi.

    Returns:
        tuple[bool, str | None]: (True, None) if successful or no relevant input.
                                 (False, error_message) if invalid enum value.
    """
    try:
        month_str = input_data.get(f"{prefix}_traditional_month")
        if month_str and month_str != month_enum.Name(
            0
        ):  # Check against default "UNKNOWN"
            try:
                trad_date_proto.month = month_enum.Value(month_str)
            except ValueError:
                return (
                    False,
                    f"Invalid traditional month value '{month_str}' for prefix '{prefix}'.",
                )

        if star_enum:
            star_str = input_data.get(f"{prefix}_traditional_star")
            if star_str and star_str != star_enum.Name(0):
                try:
                    trad_date_proto.star = star_enum.Value(star_str)
                except ValueError:
                    return (
                        False,
                        f"Invalid traditional star value '{star_str}' for prefix '{prefix}'.",
                    )

        if paksham_enum:
            paksham_str = input_data.get(f"{prefix}_traditional_paksham")
            if paksham_str and paksham_str != paksham_enum.Name(0):
                try:
                    trad_date_proto.paksham = paksham_enum.Value(paksham_str)
                except ValueError:
                    return (
                        False,
                        f"Invalid traditional paksham value '{paksham_str}' for prefix '{prefix}'.",
                    )

        if thithi_enum:
            thithi_str = input_data.get(f"{prefix}_traditional_thithi")
            if thithi_str and thithi_str != thithi_enum.Name(0):
                try:
                    trad_date_proto.thithi = thithi_enum.Value(thithi_str)
                except ValueError:
                    return (
                        False,
                        f"Invalid traditional thithi value '{thithi_str}' for prefix '{prefix}'.",
                    )
        return True, None
    except Exception as e:
        logger.exception(
            f"Unexpected error validating/populating traditional date for prefix '{prefix}': {e}"
        )
        return (
            False,
            f"An unexpected error occurred processing the traditional date for '{prefix}'.",
        )


def compare_dob_and_dod(
    member: family_tree_pb2.FamilyMember,
) -> tuple[bool | None, str]:
    """Compares Date of Birth and Date of Death for logical consistency."""
    dob_populated = member.date_of_birth.year != 0
    dod_populated = member.date_of_death.year != 0

    if dob_populated and dod_populated:
        try:
            dob = datetime.date(
                member.date_of_birth.year,
                member.date_of_birth.month,
                member.date_of_birth.date,
            )
            dod = datetime.date(
                member.date_of_death.year,
                member.date_of_death.month,
                member.date_of_death.date,
            )
            if dod < dob:
                return (
                    None,
                    "Validation Error: Date of Death cannot be before Date of Birth.",
                )
            return True, ""
        except ValueError:
            logger.error(
                "Inconsistency: Could not create date objects for comparison after individual validation passed."
            )
            return None, "Internal Error: Could not compare DOB and DOD."
    return True, ""  # Comparison not applicable or passed
