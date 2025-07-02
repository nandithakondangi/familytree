from unittest.mock import MagicMock

import google.protobuf.text_format as text_format
import pytest
from fastapi.testclient import TestClient

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree import app_state
from familytree.family_tree_webapp import app
from familytree.routers import (
    get_current_family_tree_handler_dependency,
    get_new_family_tree_handler_dependency,
)


def create_weasley_family_tree_proto():
    """Creates a FamilyTree protobuf object for the Weasley family."""
    family_tree = family_tree_pb2.FamilyTree()

    # --- Members ---
    arthur = family_tree.members["ARTHW"]
    arthur.id = "ARTHW"
    arthur.name = "Arthur Weasley"
    arthur.gender = utils_pb2.MALE
    arthur.date_of_birth.year = 1950  # Approx
    arthur.date_of_birth.month = 2
    arthur.date_of_birth.date = 6
    arthur.alive = True

    molly = family_tree.members["MOLLW"]
    molly.id = "MOLLW"
    molly.name = "Molly Weasley"
    molly.nicknames.append("Mollywobbles")
    molly.gender = utils_pb2.FEMALE
    molly.date_of_birth.year = 1949  # Approx
    molly.date_of_birth.month = 10
    molly.date_of_birth.date = 30
    molly.alive = True

    bill = family_tree.members["BILLW"]
    bill.id = "BILLW"
    bill.name = "Bill Weasley"
    bill.gender = utils_pb2.MALE
    bill.date_of_birth.year = 1970
    bill.date_of_birth.month = 11
    bill.date_of_birth.date = 29
    bill.alive = True

    charlie = family_tree.members["CHARW"]
    charlie.id = "CHARW"
    charlie.name = "Charlie Weasley"
    charlie.gender = utils_pb2.MALE
    charlie.date_of_birth.year = 1972
    charlie.date_of_birth.month = 12
    charlie.date_of_birth.date = 12
    charlie.alive = True

    percy = family_tree.members["PERCW"]
    percy.id = "PERCW"
    percy.name = "Percy Weasley"
    percy.gender = utils_pb2.MALE
    percy.date_of_birth.year = 1976
    percy.date_of_birth.month = 8
    percy.date_of_birth.date = 22
    percy.alive = True

    fred = family_tree.members["FREDW"]
    fred.id = "FREDW"
    fred.name = "Fred Weasley"
    fred.gender = utils_pb2.MALE
    fred.date_of_birth.year = 1978
    fred.date_of_birth.month = 4
    fred.date_of_birth.date = 1
    fred.alive = False  # Died in Battle of Hogwarts
    fred.date_of_death.year = 1998
    fred.date_of_death.month = 5
    fred.date_of_death.date = 2

    george = family_tree.members["GEORW"]
    george.id = "GEORW"
    george.name = "George Weasley"
    george.gender = utils_pb2.MALE
    george.date_of_birth.year = 1978
    george.date_of_birth.month = 4
    george.date_of_birth.date = 1
    george.alive = True

    ron = family_tree.members["RONAW"]
    ron.id = "RONAW"
    ron.name = "Ron Weasley"
    ron.nicknames.append("Won-Won")
    ron.gender = utils_pb2.MALE
    ron.date_of_birth.year = 1980
    ron.date_of_birth.month = 3
    ron.date_of_birth.date = 1
    ron.alive = True

    ginny = family_tree.members["GINNW"]
    ginny.id = "GINNW"
    ginny.name = "Ginny Weasley"
    ginny.gender = utils_pb2.FEMALE
    ginny.date_of_birth.year = 1981
    ginny.date_of_birth.month = 8
    ginny.date_of_birth.date = 11
    ginny.alive = True
    ginny.traditional_date_of_birth.month = utils_pb2.CHITHIRAI
    ginny.traditional_date_of_birth.star = utils_pb2.ASHWINI

    # --- Relationships (same as in tests/handlers/conftest.py for consistency) ---
    arthur_rel = family_tree.relationships["ARTHW"]
    arthur_rel.spouse_ids.append("MOLLW")
    arthur_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    molly_rel = family_tree.relationships["MOLLW"]
    molly_rel.spouse_ids.append("ARTHW")
    molly_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    children_ids = ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    for child_id in children_ids:
        child_rel = family_tree.relationships[child_id]
        child_rel.parent_ids.append("ARTHW")
        child_rel.parent_ids.append("MOLLW")

    return family_tree


@pytest.fixture
def weasley_family_tree_pb():
    """Provides a FamilyTree protobuf object for the Weasley family."""
    return create_weasley_family_tree_proto()


@pytest.fixture
def weasley_family_tree_textproto(weasley_family_tree_pb):
    """Provides the Weasley family tree as a text protobuf string."""
    return text_format.MessageToString(weasley_family_tree_pb, as_utf8=True)


@pytest.fixture(autouse=True)
def reset_app_state_between_tests():
    """Ensures app_state is reset before and after each test in this module/directory."""
    app_state.reset_current_family_tree_handler()
    yield
    app_state.reset_current_family_tree_handler()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_family_tree_handler():
    """Mocks the FamilyTreeHandler instance."""
    return MagicMock()


@pytest.fixture(name="client_with_mock_handler")
def client_with_mock_handler_fixture(mock_family_tree_handler):
    """
    Provides a TestClient where the FamilyTreeHandler dependencies are
    overridden with a mock instance. This is the correct way to test
    FastAPI dependencies, avoiding issues with patching.
    """

    def override_get_handler():
        """Returns the mock handler for standard endpoints."""
        return mock_family_tree_handler

    def override_get_new_handler():
        """Returns the mock handler for endpoints that create a new tree."""
        mock_family_tree_handler.reset_mock()  # Allow tests to verify reset behavior
        return mock_family_tree_handler

    # Apply the overrides to the app
    app.dependency_overrides[get_current_family_tree_handler_dependency] = (
        override_get_handler
    )
    app.dependency_overrides[get_new_family_tree_handler_dependency] = (
        override_get_new_handler
    )

    yield TestClient(app, raise_server_exceptions=False)

    # Clean up the overrides after the test is done
    app.dependency_overrides.clear()
