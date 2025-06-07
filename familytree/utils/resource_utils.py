import logging
import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


def get_resource(resource_name: str | None = None) -> pathlib.Path:
    """
    Gets the path to a resource file or the resources directory.
    Assumes 'resources' directory is in the project root (parent of 'familytree' directory).

    Args:
        resource_name: Optional name of the resource file.

    Returns:
        pathlib.Path object to the resource if resource_name is provided.
        str path to the resources directory if resource_name is None.
    """
    current_file_dir = pathlib.Path(__file__).parent.resolve()
    familytree_dir = current_file_dir.parent
    project_root_dir = familytree_dir.parent

    resource_dir_path = project_root_dir / "resources"

    if not resource_name:
        return resource_dir_path
    return resource_dir_path / resource_name


def get_default_images() -> tuple[dict[str, str], str]:
    """Gets paths for default local images."""
    base_path = "/images/"
    default_images = {}
    default_image_files = {
        "MALE": "male.png",
        "FEMALE": "female.png",
        "OTHER": "person.jpg",
        "GENDER_UNKNOWN": "person.jpg",
    }
    broken_image_file = "broken.gif"

    default_images = {
        key: base_path + value for key, value in default_image_files.items()
    }
    broken_image_path_str = base_path + broken_image_file
    return default_images, broken_image_path_str


def get_info_about_this_software(temp_dir_path: str = "UNKNOWN") -> str:
    """Renders the 'About' section HTML content using a Jinja2 template."""
    resources_dir_path = get_resource()
    template_loader = FileSystemLoader(searchpath=resources_dir_path)
    jinja_env = Environment(
        loader=template_loader, autoescape=select_autoescape(["html", "xml", "js"])
    )
    template_name = "about_section.html.template"
    try:
        template = jinja_env.get_template(template_name)
        return template.render(temp_dir=temp_dir_path)
    except Exception as e:
        logger.error(f"Error rendering about_section template: {e}")
        return f"<p>Error loading 'About' information: {e}</p>"
