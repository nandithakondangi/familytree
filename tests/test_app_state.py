from unittest.mock import MagicMock, patch

import pytest

from familytree.app_state import (
    GlobalAppState,
    get_current_family_tree_handler,
    global_app_state,
    reset_current_family_tree_handler,
    set_current_family_tree_handler,
)
from familytree.handlers.family_tree_handler import FamilyTreeHandler


@pytest.fixture(autouse=True)
def reset_global_state_for_tests():
    """Ensures global_app_state is reset before and after each test."""
    original_handler = global_app_state.family_tree_handler
    global_app_state.family_tree_handler = None  # Start fresh
    yield
    global_app_state.family_tree_handler = (
        original_handler  # Restore original state if any
    )


def test_global_app_state_init():
    """Tests the initial state of GlobalAppState."""
    state = GlobalAppState()
    assert state.family_tree_handler is None


def test_global_app_state_set_and_get_handler():
    """Tests setting and getting the handler in GlobalAppState."""
    state = GlobalAppState()
    mock_handler = MagicMock(spec=FamilyTreeHandler)
    state.set_handler(mock_handler)
    assert state.get_handler() is mock_handler


@patch("familytree.app_state.FamilyTreeHandler")
def test_global_app_state_get_handler_lazy_initialization(MockFamilyTreeHandler):
    """Tests lazy initialization of FamilyTreeHandler in get_handler."""
    mock_instance = MockFamilyTreeHandler.return_value
    state = GlobalAppState()
    assert state.family_tree_handler is None
    handler = state.get_handler()
    assert handler is mock_instance
    assert state.family_tree_handler is mock_instance
    MockFamilyTreeHandler.assert_called_once()


def test_get_current_family_tree_handler_uses_global_state():
    """Tests that get_current_family_tree_handler uses the global_app_state."""
    mock_handler = MagicMock(spec=FamilyTreeHandler)
    global_app_state.set_handler(mock_handler)
    assert get_current_family_tree_handler() is mock_handler


def test_set_current_family_tree_handler_updates_global_state():
    """Tests that set_current_family_tree_handler updates the global_app_state."""
    mock_handler = MagicMock(spec=FamilyTreeHandler)
    set_current_family_tree_handler(mock_handler)
    assert global_app_state.family_tree_handler is mock_handler


@patch("familytree.app_state.FamilyTreeHandler")
def test_reset_current_family_tree_handler(MockFamilyTreeHandler):
    """Tests that reset_current_family_tree_handler creates and sets a new handler."""
    initial_mock_handler = MagicMock(spec=FamilyTreeHandler)
    global_app_state.set_handler(initial_mock_handler)  # Set an initial handler

    new_mock_instance = MockFamilyTreeHandler.return_value
    reset_current_family_tree_handler()

    MockFamilyTreeHandler.assert_called_once()
    assert global_app_state.family_tree_handler is new_mock_instance
    assert global_app_state.family_tree_handler is not initial_mock_handler
