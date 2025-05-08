import datetime
import pathlib
from unittest.mock import patch

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.utils import (
    DateUtility,
    ProtoUtility,
    ResourceUtility,
)


# --- Test DateUtility ---
class TestDateUtility:
    def test_populate_gregorian_date_valid(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {"dob_date": 15, "dob_month": 6, "dob_year": 1990}
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is True
        assert error is None
        assert date_proto.date == 15
        assert date_proto.month == 6
        assert date_proto.year == 1990

    def test_populate_gregorian_date_empty_input(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {}  # No date parts
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is True
        assert error is None
        assert date_proto.year == 0  # Should remain unpopulated

    def test_populate_gregorian_date_incomplete(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {"dob_month": 6, "dob_year": 1990}  # Missing day
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is False
        assert "Incomplete Gregorian date" in error

    def test_populate_gregorian_date_invalid_day(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {"dob_date": 31, "dob_month": 2, "dob_year": 1990}  # Feb 31
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is False
        assert "Invalid day (31) for 'dob' month 2" in error

    def test_populate_gregorian_date_invalid_month(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {"dob_date": 15, "dob_month": 13, "dob_year": 1990}
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is False
        assert "Invalid month (13)" in error

    def test_populate_gregorian_date_future_date(self):
        date_proto = utils_pb2.GregorianDate()
        future_year = datetime.date.today().year + 1
        input_data = {"dob_date": 1, "dob_month": 1, "dob_year": future_year}
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is False
        assert "cannot be in the future" in error

    def test_populate_gregorian_date_non_numeric(self):
        date_proto = utils_pb2.GregorianDate()
        input_data = {"dob_date": "fifteen", "dob_month": 6, "dob_year": 1990}
        success, error = DateUtility.populate_gregorian_date(
            date_proto, input_data, "dob"
        )
        assert success is False
        assert "Non-numeric value encountered" in error

    def test_populate_traditional_date_valid_dob(self):
        trad_date_proto = utils_pb2.TraditionalDate()
        input_data = {
            "dob_traditional_month": "CHITHIRAI",
            "dob_traditional_star": "ASHWINI",
        }
        success, error = DateUtility.populate_traditional_date(
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

    def test_populate_traditional_date_valid_dod(self):
        trad_date_proto = utils_pb2.TraditionalDate()
        input_data = {
            "dod_traditional_month": "VAIKASI",
            "dod_traditional_paksham": "SHUKLA",
            "dod_traditional_thithi": "PRATHAMAI",
        }
        success, error = DateUtility.populate_traditional_date(
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

    def test_populate_traditional_date_invalid_enum_value(self):
        trad_date_proto = utils_pb2.TraditionalDate()
        input_data = {"dob_traditional_month": "INVALID_MONTH"}
        success, error = DateUtility.populate_traditional_date(
            trad_date_proto,
            input_data,
            "dob",
            utils_pb2.TamilMonth,
            star_enum=utils_pb2.TamilStar,
        )
        assert success is False
        assert "Invalid traditional month value 'INVALID_MONTH'" in error

    def test_populate_traditional_date_empty_input(self):
        trad_date_proto = utils_pb2.TraditionalDate()
        input_data = {}
        success, error = DateUtility.populate_traditional_date(
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

    def test_compare_dob_and_dod_valid(self):
        member = family_tree_pb2.FamilyMember()
        member.date_of_birth.year = 1990
        member.date_of_birth.month = 1
        member.date_of_birth.date = 1
        member.date_of_death.year = 2020
        member.date_of_death.month = 1
        member.date_of_death.date = 1
        success, error = DateUtility.compare_dob_and_dod(member)
        assert success is True
        assert error == ""

    def test_compare_dob_and_dod_invalid_dod_before_dob(self):
        member = family_tree_pb2.FamilyMember()
        member.date_of_birth.year = 2000
        member.date_of_birth.month = 1
        member.date_of_birth.date = 1
        member.date_of_death.year = 1999
        member.date_of_death.month = 1
        member.date_of_death.date = 1
        success, error = DateUtility.compare_dob_and_dod(member)
        assert (
            success is None
        )  # Or False, depending on how you want to interpret the return
        assert "Date of Death cannot be before Date of Birth" in error

    def test_compare_dob_and_dod_only_dob(self):
        member = family_tree_pb2.FamilyMember()
        member.date_of_birth.year = 1990
        member.date_of_birth.month = 1
        member.date_of_birth.date = 1
        # No DoD
        success, error = DateUtility.compare_dob_and_dod(member)
        # This case isn't explicitly handled to return an error by compare_dob_and_dod
        # It implicitly passes as the condition `dob_populated and dod_populated` is false.
        # Depending on desired behavior, this test might need adjustment or the function.
        # For now, assuming it doesn't raise an error.
        assert (
            error != "Validation Error: Date of Death cannot be before Date of Birth."
        )


# --- Test ProtoUtility ---
class TestProtoUtility:
    def test_get_enum_values_from_proto_schema_valid(self):
        genders = ProtoUtility.get_enum_values_from_proto_schema("Gender")
        assert "MALE" in genders
        assert "FEMALE" in genders
        assert "GENDER_UNKNOWN" in genders

        months = ProtoUtility.get_enum_values_from_proto_schema("TamilMonth")
        assert "CHITHIRAI" in months
        assert "TAMIL_MONTH_UNKNOWN" in months

    def test_get_enum_values_from_proto_schema_invalid_enum_name(self):
        invalid_enum_values = ProtoUtility.get_enum_values_from_proto_schema(
            "NonExistentEnum"
        )
        assert invalid_enum_values == []

    def test_get_enum_values_from_proto_schema_different_module(self):
        # Example if you had enums in family_tree_pb2
        # For now, let's test with a known one from utils_pb2 again
        stars = ProtoUtility.get_enum_values_from_proto_schema(
            "TamilStar", proto_module=utils_pb2
        )
        assert "ASHWINI" in stars
        assert "TAMIL_STAR_UNKNOWN" in stars


# --- Test ResourceUtility ---
class TestResourceUtility:
    @patch("pathlib.Path.is_file")
    def test_get_resource_with_name(self, mock_is_file, tmp_path):
        mock_is_file.return_value = True  # Assume file exists for path construction
        # We need to ensure the base 'resources' dir is mocked or correctly determined
        # For simplicity, let's assume the path construction logic in ResourceUtility is correct
        # and focus on whether it appends the resource_name.

        # Get the project root relative to this test file
        test_file_path = pathlib.Path(
            __file__
        ).resolve()  # /mnt/c/.../tests/test_utils.py
        project_root = test_file_path.parent.parent  # /mnt/c/.../FamilyTree
        expected_resource_path = project_root / "resources" / "test_file.txt"

        actual_path = ResourceUtility.get_resource("test_file.txt")
        assert actual_path == expected_resource_path

    def test_get_resource_without_name(self, tmp_path):
        test_file_path = pathlib.Path(__file__).resolve()
        project_root = test_file_path.parent.parent
        expected_resource_dir = project_root / "resources"

        actual_dir = ResourceUtility.get_resource()
        assert actual_dir == str(
            expected_resource_dir
        )  # get_resource returns str if no name

    @patch("familytree.utils.ResourceUtility.get_resource")
    @patch("pathlib.Path.is_file", autospec=True)
    def test_get_default_images_all_exist(self, mock_is_file, mock_get_resource):
        mock_is_file.return_value = True  # All image files exist

        # Define what get_resource should return for each image name
        def side_effect_get_resource(filename):
            base = pathlib.Path("/fake/resources")
            return base / filename

        mock_get_resource.side_effect = side_effect_get_resource

        default_images, broken_image = ResourceUtility.get_default_images()

        assert default_images["MALE"] == "/fake/resources/male.png"
        assert default_images["FEMALE"] == "/fake/resources/female.png"
        assert default_images["OTHER"] == "/fake/resources/person.jpg"
        assert broken_image == "/fake/resources/broken.gif"

    @patch("familytree.utils.ResourceUtility.get_resource")
    @patch("pathlib.Path.is_file", autospec=True)
    def test_get_default_images_some_missing(self, mock_is_file, mock_get_resource):
        # Simulate female.png missing, broken.gif existing
        def side_effect_is_file(path_obj):
            if path_obj.name == "female.png":
                return False
            return True

        mock_is_file.side_effect = side_effect_is_file

        def side_effect_get_resource(filename):
            base = pathlib.Path("/fake/resources")
            return base / filename

        mock_get_resource.side_effect = side_effect_get_resource

        default_images, broken_image = ResourceUtility.get_default_images()

        assert default_images["MALE"] == "/fake/resources/male.png"
        assert "FEMALE" not in default_images  # Should not be added if file missing
        assert broken_image == "/fake/resources/broken.gif"

    @patch("familytree.utils.ResourceUtility.get_resource")
    @patch("jinja2.Environment.get_template")
    def test_get_info_about_this_software(self, mock_get_template, mock_get_resource):
        # Mock get_resource to return a dummy path for the resources directory
        mock_get_resource.return_value = "/fake/resources"

        # Mock the template object and its render method
        mock_template_obj = mock_get_template.return_value
        mock_template_obj.render.return_value = (
            "<html><body>Test About Content</body></html>"
        )

        temp_dir = "/test/temp/dir"
        content = ResourceUtility.get_info_about_this_software(temp_dir_path=temp_dir)

        assert "Test About Content" in content
        mock_get_template.assert_called_once_with("about_section.html.template")
        mock_template_obj.render.assert_called_once_with(temp_dir=temp_dir)
