import os
from unittest.mock import patch
from io import StringIO
import google.protobuf.text_format as text_format
import pytest
from family_tree_pb2 import FamilyTree
from family_tree_handler import FamilyTreeHandler


# --- Fixture ---
@pytest.fixture
def family_tree_handler():
    # Create a dummy data file for testing
    test_data_file = "test_data.txtpb"
    test_output_file = "test_family_tree.html"
    create_test_data_file(test_data_file)
    handler = FamilyTreeHandler(input_file=test_data_file, output_file=test_output_file)

    yield handler, test_data_file, test_output_file

    # Cleanup
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

    if os.path.exists(test_output_file):
        os.remove(test_output_file)


# --- Helper Function ---
def create_test_data_file(test_data_file):
    # Create a simple family tree for testing
    family_tree = FamilyTree()

    # Member 1
    member1 = family_tree.members["member1"]
    member1.id = "member1"
    member1.name = "Alice"
    member1.date_of_birth.year = 1991
    member1.date_of_birth.month = 1
    member1.date_of_birth.date = 1

    # Member 2
    member2 = family_tree.members["member2"]
    member2.id = "member2"
    member2.name = "Bob"
    member2.date_of_birth.year = 1990
    member2.date_of_birth.month = 5
    member2.date_of_birth.date = 31

    # Member 3
    member3 = family_tree.members["member3"]
    member3.id = "member3"
    member3.name = "Charlie"
    member2.date_of_birth.year = 2015
    member2.date_of_birth.month = 12
    member2.date_of_birth.date = 15

    # Relationships
    relationships1 = family_tree.relationships["member1"]
    relationships1.spouse_ids.append("member2")
    relationships1.children_ids.append("member3")

    relationships2 = family_tree.relationships["member2"]
    relationships2.spouse_ids.append("member1")
    relationships2.children_ids.append("member3")

    # write the text file into the input_data directory
    with open(f"{test_data_file}", "w") as f:
        f.write(text_format.MessageToString(family_tree))


# --- Test Functions ---
def test_load_from_protobuf(family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    assert len(handler.family_tree.members) == 3
    assert len(handler.family_tree.relationships) == 2
    assert "member1" in handler.family_tree.members
    assert "member2" in handler.family_tree.members
    assert "member3" in handler.family_tree.members


def test_populate_nodes_and_edges(family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    # Check if nodes are added
    assert len(handler.nx_graph.nodes) == 3
    assert "member1" in handler.nx_graph.nodes
    assert "member2" in handler.nx_graph.nodes
    assert "member3" in handler.nx_graph.nodes

    # Check if edges are added
    assert len(handler.nx_graph.edges) == 4
    assert ("member1", "member2") in handler.nx_graph.edges
    assert ("member2", "member1") in handler.nx_graph.edges
    assert ("member1", "member3") in handler.nx_graph.edges
    assert ("member2", "member3") in handler.nx_graph.edges


@patch("builtins.input", side_effect=["Alice"])
@patch("sys.stdout", new_callable=StringIO)
def test_find_person_found(mock_stdout, mock_input, family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    handler.find_person()
    expected_output = """Person 'Alice' found in the family tree."""
    assert expected_output in mock_stdout.getvalue()


@patch("builtins.input", side_effect=["NonExistent"])
@patch("sys.stdout", new_callable=StringIO)
def test_find_person_not_found(mock_stdout, mock_input, family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    handler.find_person()
    assert (
        "Person 'NonExistent' not found in the family tree." in mock_stdout.getvalue()
    )


@patch("sys.stdout", new_callable=StringIO)
def test_display_family_tree(mock_stdout, family_tree_handler):
    handler, _, output_file = family_tree_handler
    handler.load_from_protobuf()
    handler.display_family_tree()
    assert os.path.exists(output_file)


def test_populate_nodes_and_edges_assert(family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    with pytest.raises(AssertionError):
        handler.family_tree.members["member1"].id = "wrong_id"
        handler.populate_nodes_and_edges()


@patch("sys.stdout", new_callable=StringIO)
def test_load_from_protobuf_success_message(mock_stdout, family_tree_handler):
    handler, test_data_file, _ = family_tree_handler
    handler.load_from_protobuf()
    assert f"Successfully loaded {test_data_file}" in mock_stdout.getvalue()


def test_load_from_protobuf_file_not_found(family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.update_data_source("nonexistent_file.txtpb")
    # Create a temporary file with some data
    with pytest.raises(FileNotFoundError) as context:
        handler.load_from_protobuf()
    print("foo")
    print(context.value)
    assert "No such file or directory" in str(context.value)


@patch("sys.stdout", new_callable=StringIO)
def test_print_member_details(mock_stdout, family_tree_handler):
    handler, _, _ = family_tree_handler
    handler.load_from_protobuf()
    handler.print_member_details("member1")
    expected_output = """id: "member1"\nname: "Alice"\ndate_of_birth {\n  year: 1991\n  month: 1\n  date: 1\n}"""
    assert expected_output in mock_stdout.getvalue()


def test_update_data_source(family_tree_handler):
    handler, _, _ = family_tree_handler
    new_file_path = "new_test_data.txtpb"
    create_test_data_file(new_file_path)
    handler.update_data_source(new_file_path)
    assert handler.input_file == new_file_path
    os.remove(new_file_path)


def test_update_output_file(family_tree_handler):
    handler, _, _ = family_tree_handler
    new_output_file = "new_output_file.html"
    handler.update_output_file(new_output_file)
    assert handler.output_file == new_output_file


@patch("sys.stdout", new_callable=StringIO)
def test_display_family_tree_correct_path(mock_stdout, family_tree_handler):
    handler, test_data_file, output_file = family_tree_handler
    handler.load_from_protobuf()

    # Mock the correct path for the file
    with patch.dict("os.environ", {"BUILD_WORKING_DIRECTORY": "."}):
        handler.display_family_tree()

    assert os.path.exists(output_file)
    assert os.path.realpath(output_file) == handler.output_file

    # Clean up the created file
    if os.path.exists(output_file):
        os.remove(output_file)
