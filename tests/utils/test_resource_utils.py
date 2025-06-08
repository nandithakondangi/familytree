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


def test_get_default_images_all_exist():
    default_images, broken_image = get_default_images()

    assert default_images["MALE"] == "/images/male.png"
    assert default_images["FEMALE"] == "/images/female.png"
    assert default_images["OTHER"] == "/images/person.jpg"
    assert default_images["GENDER_UNKNOWN"] == "/images/person.jpg"
    assert broken_image == "/images/broken.gif"


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
