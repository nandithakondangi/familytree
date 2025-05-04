import datetime
import logging
import os
import pathlib

# Get a logger instance for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import proto.family_tree_pb2 as family_tree_pb2


class ResourceUtility:
    """Class for handling resources."""

    @staticmethod
    def get_resource(resource_name=None):
        # Use pathlib for more robust path handling
        script_dir = pathlib.Path(__file__).parent.resolve()  # familytree directory
        base_dir = script_dir.parent  # Project root directory
        resource_dir = os.path.join(base_dir, "resources")
        if not resource_name:
            return resource_dir
        else:
            return pathlib.Path(resource_dir) / resource_name

    @staticmethod
    def get_default_images():
        """Gets paths for default local images."""
        default_images = {}
        brokenImage = ""
        try:
            default_image_files = {
                "MALE": "male.png",
                "FEMALE": "female.png",
                "OTHER": "person.jpg",
                "GENDER_UNKNOWN": "person.jpg",
            }
            broken_image_file = "broken.gif"

            for key, filename in default_image_files.items():
                path = ResourceUtility.get_resource(filename)
                if path.is_file():
                    default_images[key] = str(path)  # Store as string path
                else:
                    logger.warning(f"Default image not found for {key} at {path}")

            broken_path = ResourceUtility.get_resource(broken_image_file)
            if broken_path.is_file():
                brokenImage = str(broken_path)
            else:
                logger.warning(f"Broken image not found at {broken_path}")

        except Exception as e:
            logger.error(f"Error determining default image paths: {e}")
            # Return empty dicts/strings on error
            default_images = {}
            brokenImage = ""

        return default_images, brokenImage


class DateUtility:
    """
    Utility class for handling date parsing, validation, and population
    for FamilyMember protobufs.
    Methods return a tuple: (success: bool, error_message: str | None).
    """

    @staticmethod
    def populate_gregorian_date(
        date_proto, input_data, prefix
    ) -> tuple[bool, str | None]:
        """
        Populates and validates a GregorianDate protobuf message from input data.

        Args:
            date_proto: The GregorianDate message to populate (e.g., member.date_of_birth).
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").

        Returns:
            tuple[bool, str | None]: (True, None) if the date was successfully populated
                                     or no relevant input was found.
                                     (False, error_message) if invalid data was provided.
        """
        day_str = input_data.get(f"{prefix}_date")
        month_str = input_data.get(f"{prefix}_month")
        year_str = input_data.get(f"{prefix}_year")

        # Check if any date part was actually provided (treat empty strings as not provided)
        if not (day_str or month_str or year_str):
            return True, None  # No data provided, nothing to validate or set, success.

        try:
            # Attempt conversion, default to 0 if empty string or None
            day = int(day_str or 0)
            month = int(month_str or 0)
            year = int(year_str or 0)

            # Ensure all parts were provided if at least one was
            if not (day and month and year):
                return (
                    False,
                    f"Incomplete Gregorian date provided for '{prefix}'. Please provide day, month, and year.",
                )

            # --- Comprehensive Validation ---
            # 1. Use datetime for calendar validity (handles leap years, days in month)
            try:
                parsed_date = datetime.date(year, month, day)
            except ValueError as e:
                # More specific error based on common ValueError messages
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
                elif "year" in str(e):  # Catch other year-related errors if any
                    return False, f"Invalid year ({year}) provided for '{prefix}'. {e}"
                else:  # Generic fallback
                    return (
                        False,
                        f"Invalid Gregorian date for '{prefix}': Day={day}, Month={month}, Year={year}. Reason: {e}",
                    )

            # 2. Check if the date is in the future
            if parsed_date > datetime.date.today():
                return (
                    False,
                    f"Gregorian date for '{prefix}' ({parsed_date.strftime('%Y-%m-%d')}) cannot be in the future.",
                )

            # 3. Check for reasonably sensible year (optional, adjust as needed)
            if year < 1000:  # Or some other sensible minimum year
                return (
                    False,
                    f"Year ({year}) for '{prefix}' seems too far in the past. Please check.",
                )
            # --- End Validation ---

            # If all checks pass, populate the proto
            date_proto.date = day
            date_proto.month = month
            date_proto.year = year
            return True, None  # Successfully populated

        except (ValueError, TypeError):
            # Catches errors during int() conversion if non-numeric provided
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
            )  # Generic message for unexpected

    @staticmethod
    def populate_traditional_date(
        trad_date_proto,
        input_data,
        prefix,
        month_enum,
        star_enum=None,
        paksham_enum=None,
        thithi_enum=None,
    ) -> tuple[bool, str | None]:
        """
        Populates and validates a TraditionalDate protobuf message from input data using enums.

        Args:
            trad_date_proto: The TraditionalDate message to populate.
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").
            month_enum: The protobuf enum type for the Tamil month.
            star_enum: Optional protobuf enum type for the Tamil star.
            paksham_enum: Optional protobuf enum type for Paksham.
            thithi_enum: Optional protobuf enum type for Thithi.

        Returns:
            tuple[bool, str | None]: (True, None) if the date was successfully populated
                                     or no relevant input was found.
                                     (False, error_message) if an invalid enum value string was provided.
        """
        try:
            field_updated = False  # Track if we actually set any field

            # --- Month ---
            month_str = input_data.get(f"{prefix}_traditional_month")
            if month_str and month_str != month_enum.Name(
                0
            ):  # Check against default "UNKNOWN"
                try:
                    trad_date_proto.month = month_enum.Value(month_str)
                    field_updated = True
                except ValueError:
                    return (
                        False,
                        f"Invalid traditional month value '{month_str}' for prefix '{prefix}'.",
                    )

            # --- Star (if applicable) ---
            if star_enum:
                star_str = input_data.get(f"{prefix}_traditional_star")
                if star_str and star_str != star_enum.Name(0):
                    try:
                        trad_date_proto.star = star_enum.Value(star_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional star value '{star_str}' for prefix '{prefix}'.",
                        )

            # --- Paksham (if applicable) ---
            if paksham_enum:
                paksham_str = input_data.get(f"{prefix}_traditional_paksham")
                if paksham_str and paksham_str != paksham_enum.Name(0):
                    try:
                        trad_date_proto.paksham = paksham_enum.Value(paksham_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional paksham value '{paksham_str}' for prefix '{prefix}'.",
                        )

            # --- Thithi (if applicable) ---
            if thithi_enum:
                thithi_str = input_data.get(f"{prefix}_traditional_thithi")
                if thithi_str and thithi_str != thithi_enum.Name(0):
                    try:
                        trad_date_proto.thithi = thithi_enum.Value(thithi_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional thithi value '{thithi_str}' for prefix '{prefix}'.",
                        )

            # If we reached here without returning False, validation passed for provided fields
            return True, None

        except Exception as e:
            logger.exception(
                f"Unexpected error validating/populating traditional date for prefix '{prefix}': {e}"
            )
            return (
                False,
                f"An unexpected error occurred processing the traditional date for '{prefix}'.",
            )

    @staticmethod
    def compare_dob_and_dod(
        member: family_tree_pb2.FamilyMember,
    ) -> tuple[bool | None, str]:
        # --- DOD vs DOB Check (after both are potentially populated) ---
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
                else:
                    return True, ""
            except ValueError:
                logger.error(
                    "Inconsistency: Could not create date objects for comparison after individual validation passed."
                )
                return None, "Internal Error: Could not compare DOB and DOD."
