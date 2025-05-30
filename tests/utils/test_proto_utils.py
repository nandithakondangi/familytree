import familytree.proto.utils_pb2 as utils_pb2
from familytree.utils.proto_utils import (
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
