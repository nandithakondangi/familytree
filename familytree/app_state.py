import logging
from typing import Optional

from familytree.handlers.family_tree_handler import FamilyTreeHandler

logger = logging.getLogger(__name__)


class GlobalAppState:
    def __init__(self):
        self.family_tree_handler: Optional[FamilyTreeHandler] = None
        logger.info("GlobalAppState initialized, FamilyTreeHandler is None.")

    def set_handler(self, handler: FamilyTreeHandler):
        self.family_tree_handler = handler
        logger.info(f"Global FamilyTreeHandler instance updated to: {handler}")

    def get_handler(self) -> FamilyTreeHandler:
        if self.family_tree_handler is None:
            logger.warning(
                "FamilyTreeHandler accessed before explicit initialization. Creating a default one."
            )
            self.family_tree_handler = FamilyTreeHandler()
        return self.family_tree_handler


# Single instance of our state
global_app_state = GlobalAppState()


# Dependency function for FastAPI
def get_current_family_tree_handler() -> FamilyTreeHandler:
    return global_app_state.get_handler()


def set_current_family_tree_handler(handler: FamilyTreeHandler):
    global_app_state.set_handler(handler)


def reset_current_family_tree_handler():
    logger.info("Resetting global FamilyTreeHandler.")
    new_handler = FamilyTreeHandler()
    global_app_state.set_handler(new_handler)
