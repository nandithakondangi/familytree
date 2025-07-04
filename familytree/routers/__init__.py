from familytree import app_state
from familytree.handlers.family_tree_handler import FamilyTreeHandler


def get_current_family_tree_handler_dependency() -> FamilyTreeHandler:
    """Dependency to get the current family tree handler."""
    return app_state.get_current_family_tree_handler()


def get_new_family_tree_handler_dependency() -> FamilyTreeHandler:
    """Dependency to get a new family tree handler."""
    app_state.reset_current_family_tree_handler()
    return get_current_family_tree_handler_dependency()
