import pathlib
from unittest.mock import patch

from familytree.utils.resource_utils import (
    get_default_images,
    get_info_about_this_software,
    get_resource,
)


@patch("pathlib.Path.is_file")
def test_get_resource_with_name(mock_is_file):
    mock_is_file.return_value = True  # Assume file exists for path construction
    # Get the project root relative to this test file
    test_file_path = pathlib.Path(__file__).resolve()
    project_root = (
        test_file_path.parent.parent.parent
    )  # familytree -> tests -> utils -> test_resource_utils.py
    expected_resource_path = project_root / "resources" / "test_file.txt"

    actual_path = get_resource("test_file.txt")
    assert actual_path == expected_resource_path


def test_get_resource_without_name():
    test_file_path = pathlib.Path(__file__).resolve()
    project_root = test_file_path.parent.parent.parent
    expected_resource_dir = project_root / "resources"

    actual_dir = get_resource()
    assert actual_dir == expected_resource_dir


@patch("familytree.utils.resource_utils.get_resource")
@patch("pathlib.Path.is_file", autospec=True)
def test_get_default_images_all_exist(mock_is_file, mock_get_resource_func):
    mock_is_file.return_value = True  # All image files exist

    # Define what get_resource should return for each image name
    def side_effect_get_resource(filename):
        base = pathlib.Path("/fake/resources")
        return base / filename

    mock_get_resource_func.side_effect = side_effect_get_resource

    default_images, broken_image = get_default_images()

    assert default_images["MALE"] == "/fake/resources/male.png"
    assert default_images["FEMALE"] == "/fake/resources/female.png"
    assert default_images["OTHER"] == "/fake/resources/person.jpg"
    assert default_images["GENDER_UNKNOWN"] == "/fake/resources/person.jpg"
    assert broken_image == "/fake/resources/broken.gif"


@patch("familytree.utils.resource_utils.get_resource")
@patch("pathlib.Path.is_file", autospec=True)
def test_get_default_images_some_missing(mock_is_file, mock_get_resource_func):
    # Simulate female.png missing, broken.gif existing
    def side_effect_is_file(path_obj):
        if path_obj.name == "female.png":
            return False
        return True

    mock_is_file.side_effect = side_effect_is_file

    def side_effect_get_resource(filename):
        base = pathlib.Path("/fake/resources")
        return base / filename

    mock_get_resource_func.side_effect = side_effect_get_resource

    default_images, broken_image = get_default_images()

    assert default_images["MALE"] == "/fake/resources/male.png"
    assert "FEMALE" not in default_images  # Should not be added if file missing
    assert broken_image == "/fake/resources/broken.gif"


@patch("familytree.utils.resource_utils.get_resource")
@patch("jinja2.Environment.get_template")
def test_get_info_about_this_software(mock_get_template, mock_get_resource_func):
    mock_get_resource_func.return_value = "/fake/resources"  # For FileSystemLoader
    mock_template_obj = mock_get_template.return_value
    mock_template_obj.render.return_value = (
        "<html><body>Test About Content</body></html>"
    )

    temp_dir = "/test/temp/dir"
    content = get_info_about_this_software(temp_dir_path=temp_dir)

    assert "Test About Content" in content
    mock_get_template.assert_called_once_with("about_section.html.template")
    mock_template_obj.render.assert_called_once_with(temp_dir=temp_dir)
