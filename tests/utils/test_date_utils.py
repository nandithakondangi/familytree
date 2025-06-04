import datetime

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.utils.date_utils import (
    compare_dob_and_dod,
    populate_gregorian_date,
    populate_traditional_date,
)


def test_populate_gregorian_date_valid():
    date_proto = utils_pb2.GregorianDate()
    input_data = {"dob_date": "15", "dob_month": "6", "dob_year": "1990"}
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is True
    assert error is None
    assert date_proto.date == 15
    assert date_proto.month == 6
    assert date_proto.year == 1990


def test_populate_gregorian_date_empty_input():
    date_proto = utils_pb2.GregorianDate()
    input_data = {}  # No date parts
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is True
    assert error is None
    assert date_proto.year == 0  # Should remain unpopulated


def test_populate_gregorian_date_incomplete():
    date_proto = utils_pb2.GregorianDate()
    input_data = {"dob_month": "6", "dob_year": "1990"}  # Missing day
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is False
    assert "Incomplete Gregorian date" in error


def test_populate_gregorian_date_invalid_day():
    date_proto = utils_pb2.GregorianDate()
    input_data = {"dob_date": "31", "dob_month": "2", "dob_year": "1990"}  # Feb 31
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is False
    assert "Invalid day (31) for 'dob' month 2" in error


def test_populate_gregorian_date_invalid_month():
    date_proto = utils_pb2.GregorianDate()
    input_data = {"dob_date": "15", "dob_month": "13", "dob_year": "1990"}
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is False
    assert "Invalid month (13)" in error


def test_populate_gregorian_date_future_date():
    date_proto = utils_pb2.GregorianDate()
    future_year = datetime.date.today().year + 1
    input_data = {"dob_date": "1", "dob_month": "1", "dob_year": str(future_year)}
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is False
    assert "cannot be in the future" in error


def test_populate_gregorian_date_non_numeric():
    date_proto = utils_pb2.GregorianDate()
    input_data = {"dob_date": "fifteen", "dob_month": "6", "dob_year": "1990"}
    success, error = populate_gregorian_date(date_proto, input_data, "dob")
    assert success is False
    assert "Non-numeric value encountered" in error


def test_populate_traditional_date_valid_dob():
    trad_date_proto = utils_pb2.TraditionalDate()
    input_data = {
        "dob_traditional_month": "CHITHIRAI",
        "dob_traditional_star": "ASHWINI",
    }
    success, error = populate_traditional_date(
        trad_date_proto,
        input_data,
        "dob",
        utils_pb2.TamilMonth,
        star_enum=utils_pb2.TamilStar,
    )
    assert success is True
    assert error is None
    assert trad_date_proto.month == utils_pb2.CHITHIRAI
    assert trad_date_proto.star == utils_pb2.ASHWINI


def test_populate_traditional_date_valid_dod():
    trad_date_proto = utils_pb2.TraditionalDate()
    input_data = {
        "dod_traditional_month": "VAIKASI",
        "dod_traditional_paksham": "SHUKLA",
        "dod_traditional_thithi": "PRATHAMAI",
    }
    success, error = populate_traditional_date(
        trad_date_proto,
        input_data,
        "dod",
        utils_pb2.TamilMonth,
        paksham_enum=utils_pb2.Paksham,
        thithi_enum=utils_pb2.Thithi,
    )
    assert success is True
    assert error is None
    assert trad_date_proto.month == utils_pb2.VAIKASI
    assert trad_date_proto.paksham == utils_pb2.SHUKLA
    assert trad_date_proto.thithi == utils_pb2.PRATHAMAI


def test_populate_traditional_date_invalid_enum_value():
    trad_date_proto = utils_pb2.TraditionalDate()
    input_data = {"dob_traditional_month": "INVALID_MONTH"}
    success, error = populate_traditional_date(
        trad_date_proto,
        input_data,
        "dob",
        utils_pb2.TamilMonth,
        star_enum=utils_pb2.TamilStar,
    )
    assert success is False
    assert "Invalid traditional month value 'INVALID_MONTH'" in error


def test_populate_traditional_date_empty_input():
    trad_date_proto = utils_pb2.TraditionalDate()
    input_data = {}
    success, error = populate_traditional_date(
        trad_date_proto,
        input_data,
        "dob",
        utils_pb2.TamilMonth,
        star_enum=utils_pb2.TamilStar,
    )
    assert success is True
    assert error is None
    assert (
        trad_date_proto.month == utils_pb2.TAMIL_MONTH_UNKNOWN
    )  # Should remain default


def test_compare_dob_and_dod_valid():
    member = family_tree_pb2.FamilyMember()
    member.date_of_birth.year = 1990
    member.date_of_birth.month = 1
    member.date_of_birth.date = 1
    member.date_of_death.year = 2020
    member.date_of_death.month = 1
    member.date_of_death.date = 1
    success, error_msg = compare_dob_and_dod(member)
    assert success is True
    assert error_msg == ""


def test_compare_dob_and_dod_invalid_dod_before_dob():
    member = family_tree_pb2.FamilyMember()
    member.date_of_birth.year = 2000
    member.date_of_birth.month = 1
    member.date_of_birth.date = 1
    member.date_of_death.year = 1999
    member.date_of_death.month = 1
    member.date_of_death.date = 1
    success, error_msg = compare_dob_and_dod(member)
    assert success is None
    assert "Date of Death cannot be before Date of Birth" in error_msg


def test_compare_dob_and_dod_only_dob():
    member = family_tree_pb2.FamilyMember()
    member.date_of_birth.year = 1990
    member.date_of_birth.month = 1
    member.date_of_birth.date = 1
    # No DoD
    success, error_msg = compare_dob_and_dod(member)
    assert success is True
    assert error_msg == ""


def test_compare_dob_and_dod_incomplete_dates():
    member = family_tree_pb2.FamilyMember()
    # DOB is populated but might be invalid if day/month is 0,
    # but compare_dob_and_dod relies on year != 0
    member.date_of_birth.year = 1990
    # DOD is not fully populated (year is 0)
    member.date_of_death.year = 0
    member.date_of_death.month = 1

    success, error_msg = compare_dob_and_dod(member)
    assert success is True  # Comparison not applicable
    assert error_msg == ""

    # Both populated but one is invalid (e.g. month=0)
    # This case should ideally be caught by populate_gregorian_date first.
    # compare_dob_and_dod might raise ValueError if date objects can't be created.
    member.date_of_birth.year = 1990
    member.date_of_birth.month = 1
    member.date_of_birth.date = 1
    member.date_of_death.year = 1995
    member.date_of_death.month = 0  # Invalid month
    member.date_of_death.date = 1

    success_val_err, error_msg_val_err = compare_dob_and_dod(member)
    assert success_val_err is None  # Due to ValueError creating date object
    assert "Internal Error: Could not compare DOB and DOD." in error_msg_val_err
