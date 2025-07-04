import pytest

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.utils.proto_utils import (
    apply_changes,
    get_enum_values_from_proto_schema,
    get_gender_name,
    get_month_name,
    get_paksham_name,
    get_star_name,
    get_thithi_name,
)


def test_get_gender_name():
    assert get_gender_name(utils_pb2.MALE) == "MALE"
    assert get_gender_name(utils_pb2.FEMALE) == "FEMALE"
    assert get_gender_name(utils_pb2.GENDER_UNKNOWN) == "GENDER_UNKNOWN"


def test_get_month_name():
    assert get_month_name(utils_pb2.CHITHIRAI) == "CHITHIRAI"
    assert get_month_name(utils_pb2.TAMIL_MONTH_UNKNOWN) == "TAMIL_MONTH_UNKNOWN"


def test_get_star_name():
    assert get_star_name(utils_pb2.ASHWINI) == "ASHWINI"
    assert get_star_name(utils_pb2.TAMIL_STAR_UNKNOWN) == "TAMIL_STAR_UNKNOWN"


def test_get_paksham_name():
    assert get_paksham_name(utils_pb2.SHUKLA) == "SHUKLA"
    assert get_paksham_name(utils_pb2.PAKSHAM_UNKNOWN) == "PAKSHAM_UNKNOWN"


def test_get_thithi_name():
    assert get_thithi_name(utils_pb2.PRATHAMAI) == "PRATHAMAI"
    assert get_thithi_name(utils_pb2.THITHI_UNKNOWN) == "THITHI_UNKNOWN"


def test_get_enum_values_from_proto_schema_valid():
    genders = get_enum_values_from_proto_schema("Gender")
    assert "MALE" in genders
    assert "FEMALE" in genders
    months = get_enum_values_from_proto_schema("TamilMonth", proto_module=utils_pb2)
    assert "CHITHIRAI" in months


def test_get_enum_values_from_proto_schema_invalid_enum_name():
    invalid_enum_values = get_enum_values_from_proto_schema("NonExistentEnum")
    assert invalid_enum_values == []


def test_apply_changes():
    """Tests that apply_changes correctly updates all field types."""
    # Setup initial message 'a'
    a = family_tree_pb2.FamilyMember()
    a.id = "1"
    a.name = "Original Name"
    a.nicknames.extend(["OG", "Original"])
    a.gender = utils_pb2.MALE
    a.date_of_birth.year = 1990
    a.additional_info["hobby"] = "reading"
    a.additional_info["pet"] = "dog"

    # Setup changes message 'b'
    b = family_tree_pb2.FamilyMember()
    b.name = "Updated Name"  # Singular field
    b.nicknames.extend(["NewNick"])  # Repeated field
    b.gender = utils_pb2.FEMALE  # Enum field
    b.date_of_birth.year = 2000  # Nested message field
    b.date_of_birth.month = 5
    b.additional_info["hobby"] = "swimming"  # Map field

    # Apply changes
    apply_changes(a, b)

    # Assertions
    assert a.id == "1"  # Unchanged field
    assert a.name == "Updated Name"  # Singular updated
    assert list(a.nicknames) == [
        "NewNick",
        "OG",
        "Original",
    ]  # Repeated fields combined without duplicates
    assert a.gender == utils_pb2.FEMALE  # Enum updated
    assert a.date_of_birth.year == 2000  # Nested updated
    assert a.date_of_birth.month == 5
    assert a.additional_info["hobby"] == "swimming"  # Map updated
    assert a.additional_info["pet"] == "dog"  # Unchanged map key field


def test_apply_changes_type_mismatch():
    """Tests that a TypeError is raised for mismatched message types."""
    a = family_tree_pb2.FamilyMember()
    b = utils_pb2.GregorianDate()  # Different type
    with pytest.raises(TypeError) as excinfo:
        apply_changes(a, b)
    assert "Messages 'a' and 'b' must be of the same type" in str(excinfo.value)


def test_apply_changes_no_changes():
    """Tests that no changes are applied if the source message is empty."""
    a = family_tree_pb2.FamilyMember()
    a.id = "1"
    a.name = "Original Name"

    a_copy = family_tree_pb2.FamilyMember()
    a_copy.CopyFrom(a)

    b = family_tree_pb2.FamilyMember()  # Empty message

    apply_changes(a, b)

    assert a == a_copy  # 'a' should be unchanged
