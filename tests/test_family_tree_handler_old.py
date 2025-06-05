import logging
import os
from unittest.mock import patch

import google.protobuf.text_format as text_format
import pytest

# Assuming protos are generated and accessible relative to the tests directory
# Adjust the import path if your structure is different
import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.family_tree_handler import FamilyTreeHandler
from familytree.graph_handler import COLOR_PALETTLE  # Moved import

# --- Test Functions ---

# --- Initialization and Loading Tests (mostly unchanged) ---


def test_init_defaults(tmp_path):
    """Test if handler initializes with correct default output paths."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    assert handler.proto_handler_instance.input_text_file is None
    assert handler.graph_handler_instance.output_html_file == os.path.join(
        tmp_path, "family_tree.html"
    )
    assert handler.proto_handler_instance.output_proto_data_file == os.path.join(
        tmp_path, "family_tree_data.txtpb"
    )
    assert not handler.proto_handler_instance.family_tree.members
    assert not handler.graph_handler_instance.nx_graph.nodes


def test_load_from_protobuf_success(weasley_handler, caplog):
    """Test successful loading of the Weasley protobuf data."""
    handler, input_file, _, _ = weasley_handler
    caplog.set_level(logging.INFO)
    handler.load_from_text_file()  # Updated method name

    assert len(handler.proto_handler_instance.family_tree.members) == 9
    assert len(handler.proto_handler_instance.family_tree.relationships) >= 2
    assert "ARTHW" in handler.proto_handler_instance.family_tree.members
    assert (
        handler.proto_handler_instance.family_tree.members["ARTHW"].name
        == "Arthur Weasley"
    )
    assert "GINNW" in handler.proto_handler_instance.family_tree.members
    assert (
        handler.proto_handler_instance.family_tree.members["GINNW"].gender
        == utils_pb2.FEMALE
    )
    assert f"Successfully loaded {input_file}" in caplog.text
    assert (
        len(handler.graph_handler_instance.nx_graph.nodes) == 9
    )  # Check graph population


def test_load_from_protobuf_file_not_found(tmp_path):
    """Test loading when the input file does not exist."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    non_existent_file = tmp_path / "ghost_file.txtpb"
    handler.proto_handler_instance.update_data_source(str(non_existent_file))

    with pytest.raises(FileNotFoundError) as excinfo:
        handler.load_from_text_file()  # Updated method name
    assert str(non_existent_file) in str(excinfo.value)


def test_load_from_protobuf_parse_error(tmp_path, caplog):
    """Test loading a file with invalid protobuf format."""
    caplog.set_level(logging.ERROR)
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    bad_file = tmp_path / "bad_format.txtpb"
    with open(bad_file, "w") as f:
        f.write("this is not protobuf text format {")

    handler.proto_handler_instance.update_data_source(str(bad_file))
    with pytest.raises(text_format.ParseError):
        handler.load_from_text_file()  # Updated method name
    assert f"Error parsing protobuf text file {bad_file}" in caplog.text


# --- Graph Population Tests (mostly unchanged) ---


def test_load_populates_graph_correctly(weasley_handler):
    """Test population of the NetworkX graph from loaded protobuf."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    graph = handler.graph_handler_instance.nx_graph

    # Check nodes
    assert len(graph.nodes) == 9
    assert "ARTHW" in graph.nodes
    assert graph.nodes["ARTHW"]["label"] == "Arthur Weasley"

    # Check spouse edges (weight=0, both directions)
    assert graph.has_edge("ARTHW", "MOLLW")
    assert graph.edges["ARTHW", "MOLLW"]["weight"] == 0
    assert graph.edges["ARTHW", "MOLLW"]["color"] == COLOR_PALETTLE["pink"]
    assert graph.has_edge("MOLLW", "ARTHW")
    assert graph.edges["MOLLW", "ARTHW"]["weight"] == 0
    assert graph.edges["MOLLW", "ARTHW"]["color"] == COLOR_PALETTLE["pink"]

    # Check visible parent -> child edge (weight=1)
    assert graph.has_edge("ARTHW", "RONAW")
    assert graph.edges["ARTHW", "RONAW"]["weight"] == 1
    assert "color" not in graph.edges["ARTHW", "RONAW"]  # Default color

    # Check hidden child -> parent edge (weight=-1)
    assert graph.has_edge("RONAW", "ARTHW")
    assert graph.edges["RONAW", "ARTHW"]["weight"] == -1
    assert "color" not in graph.edges["RONAW", "ARTHW"]

    # Check another child pair
    assert graph.has_edge("MOLLW", "GINNW")
    assert graph.edges["MOLLW", "GINNW"]["weight"] == 1
    assert graph.has_edge("GINNW", "MOLLW")
    assert graph.edges["GINNW", "MOLLW"]["weight"] == -1

    # Check total number of edges (2 between spouses + (7 parent->child + 7 child->parent) * (2 parents) = 30)
    assert graph.number_of_edges() == 30

    # Check node attributes (Ginny example)
    ginny_node = graph.nodes["GINNW"]
    assert ginny_node["label"] == "Ginny Weasley"
    assert "title" in ginny_node
    assert "Ginny Weasley" in ginny_node["title"]
    assert "FEMALE" in ginny_node["title"]
    assert "CHITHIRAI" in ginny_node["title"]


# --- Node Creation Tests (verify existing tests) ---


def test_create_member_basic(tmp_path, caplog):
    """Test creating a basic node with minimal info."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    caplog.set_level(logging.INFO)
    input_data = {"name": "Sirius Black", "gender": "MALE", "IsAlive": False}
    new_member_id_val = handler.create_member(input_data)

    assert new_member_id_val is not None
    assert len(handler.proto_handler_instance.family_tree.members) == 1
    # Get the ID of the newly created member (it's random)
    member_id = list(handler.proto_handler_instance.family_tree.members.keys())[0]

    sirius = handler.proto_handler_instance.family_tree.members[member_id]
    assert sirius.id == member_id
    assert sirius.name == "Sirius Black"
    assert sirius.gender == utils_pb2.MALE
    assert new_member_id_val == member_id
    assert not sirius.alive

    assert len(handler.graph_handler_instance.nx_graph.nodes) == 1
    assert member_id in handler.graph_handler_instance.nx_graph.nodes
    assert (
        handler.graph_handler_instance.nx_graph.nodes[member_id]["label"]
        == "Sirius Black"
    )
    assert (
        f"Successfully added member {member_id} ('Sirius Black') in prototree and graph."
        in caplog.text
    )


def test_create_member_full(tmp_path):
    """Test creating a node with more complete information."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    input_data = {
        "name": "Remus Lupin",
        "nicknames": "Moony",
        "gender": "MALE",
        "dob_date": 10,
        "dob_month": 3,
        "dob_year": 1960,
        "dob_traditional_month": "PANGUNI",
        "dob_traditional_star": "PUNARPOOSAM",
        "IsAlive": False,
        "dod_date": 2,
        "dod_month": 5,
        "dod_year": 1998,
        "dod_traditional_month": "VAIKASI",
        "dod_traditional_paksham": "KRISHNA",
        "dod_traditional_thithi": "DWITHIYAI",
    }
    new_member_id_val = handler.create_member(input_data)

    assert new_member_id_val is not None
    assert len(handler.proto_handler_instance.family_tree.members) == 1
    member_id = list(handler.proto_handler_instance.family_tree.members.keys())[0]

    lupin = handler.proto_handler_instance.family_tree.members[member_id]

    assert lupin.name == "Remus Lupin"
    assert list(lupin.nicknames) == ["Moony"]
    assert lupin.gender == utils_pb2.MALE
    assert lupin.date_of_birth.year == 1960
    assert lupin.traditional_date_of_birth.month == utils_pb2.PANGUNI
    assert not lupin.alive
    assert lupin.date_of_death.year == 1998
    assert lupin.traditional_date_of_death.paksham == utils_pb2.KRISHNA
    assert new_member_id_val == member_id

    assert member_id in handler.graph_handler_instance.nx_graph.nodes
    assert (
        handler.graph_handler_instance.nx_graph.nodes[member_id]["label"]
        == "Remus Lupin"
    )


def test_create_member_invalid_input(tmp_path, caplog):
    """Test node creation with invalid data (e.g., empty name, bad enum, bad date)."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    caplog.set_level(logging.WARNING)  # Capture warnings for invalid gender

    # Empty name
    with pytest.raises(Exception) as excinfo:
        handler.create_member({"name": "  ", "gender": "MALE"})
    assert "Validation Error: Name cannot be empty." in str(excinfo.value)
    assert len(handler.proto_handler_instance.family_tree.members) == 0

    # Invalid gender (should still create but log warning and set default)
    # create_member should succeed here as ProtoHandler.create_proto_member_from_dict handles this
    new_member_id_val = handler.create_member(
        {"name": "Nymphadora Tonks", "gender": "METAMORPHMAGUS"}
    )
    assert new_member_id_val is not None
    assert len(handler.proto_handler_instance.family_tree.members) == 1
    member_id = list(handler.proto_handler_instance.family_tree.members.keys())[0]
    tonks = handler.proto_handler_instance.family_tree.members[member_id]
    assert tonks.gender == utils_pb2.GENDER_UNKNOWN  # Should default
    assert "Invalid gender value 'METAMORPHMAGUS'" in caplog.text

    # Invalid date parts (incomplete date)
    with pytest.raises(Exception) as excinfo:
        handler.create_member(
            {"name": "Albus Dumbledore", "gender": "MALE", "dob_date": 31}
        )
    assert "Incomplete Gregorian date provided" in str(excinfo.value)
    assert len(handler.proto_handler_instance.family_tree.members) == 1  # Only Tonks

    # Invalid date value (day 31 in Feb)
    with pytest.raises(Exception) as excinfo:
        handler.create_member(
            {
                "name": "Gellert Grindelwald",
                "gender": "MALE",
                "dob_date": 31,
                "dob_month": 2,
                "dob_year": 1900,
            }
        )
    assert "Date of Birth Error: Invalid day (31) for 'dob' month 2" in str(
        excinfo.value
    )
    # Ensure create_member returns None on validation error from proto_handler
    # This requires create_member to catch the exception and return None, or for the test to expect an exception.
    # Based on current FamilyTreeHandler.create_member, it raises the exception.
    # If it were to return None, the test would be:
    # new_id = handler.create_member(...)
    # assert new_id is None

    assert len(handler.proto_handler_instance.family_tree.members) == 1  # Still Tonks


# --- Node Update Tests ---


def test_update_member_success(weasley_handler, caplog):
    """Test successfully updating an existing node."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    caplog.set_level(logging.INFO)

    ron_id = "RONAW"
    update_data = {
        "name": "Ronald Bilius Weasley",  # Change name
        "nicknames": "Won-Won, Ronnie",  # Change nicknames
        "gender": "MALE",  # Keep same
        "dob_date": 1,
        "dob_month": 3,
        "dob_year": 1980,  # Keep same
        "IsAlive": True,  # Keep same
    }

    success = handler.update_member(ron_id, update_data)
    assert success is True

    # Verify changes in protobuf
    ron_updated = handler.proto_handler_instance.family_tree.members[ron_id]
    assert ron_updated.name == "Ronald Bilius Weasley"
    assert list(ron_updated.nicknames) == ["Won-Won", "Ronnie"]

    # Verify changes in graph node
    ron_node = handler.graph_handler_instance.nx_graph.nodes[ron_id]
    assert ron_node["label"] == "Ronald Bilius Weasley"
    assert "Ronald Bilius Weasley" in ron_node["title"]
    assert "Won-Won" in ron_node["title"]
    assert "Ronnie" in ron_node["title"]

    assert (
        f"Successfully updated member {ron_id} ('Ronald Bilius Weasley') in prototree and graph."
        in caplog.text
    )


def test_update_member_change_alive_status(weasley_handler):
    """Test updating alive status and adding DoD."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    george_id = "GEORW"

    # Initially George is alive
    assert handler.proto_handler_instance.family_tree.members[george_id].alive is True
    assert not handler.proto_handler_instance.family_tree.members[george_id].HasField(
        "date_of_death"
    )

    update_data = {
        "name": "George Weasley",
        "gender": "MALE",
        "IsAlive": False,  # Change status
        "dod_date": 10,
        "dod_month": 10,
        "dod_year": 2022,  # Valid past DoD, after DoB (1978)
    }
    success = handler.update_member(george_id, update_data)
    assert success is True

    george_updated = handler.proto_handler_instance.family_tree.members[george_id]
    assert george_updated.alive is False
    assert george_updated.date_of_death.year == 2022  # Assert the year we set
    assert george_updated.date_of_death.month == 10
    assert george_updated.date_of_death.date == 10

    # Check graph title updated
    george_node = handler.graph_handler_instance.nx_graph.nodes[george_id]
    assert "Alive: False" in george_node["title"]
    # The exact string format of the date in the title might vary,
    # so check for key components.
    assert "'year': 2022" in george_node["title"]
    assert "'month': 10" in george_node["title"]
    assert "'date': 10" in george_node["title"]


def test_update_member_clear_field(weasley_handler):
    """Test that updating with empty data clears existing data."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    molly_id = "MOLLW"
    assert (
        "Mollywobbles"
        in handler.proto_handler_instance.family_tree.members[molly_id].nicknames
    )

    update_data = {
        "name": "Molly Weasley",
        "nicknames": "",  # Empty nickname string
        "gender": "FEMALE",
        "IsAlive": True,
        # No DOB provided in update
    }
    success = handler.update_member(molly_id, update_data)
    assert success is True

    molly_updated = handler.proto_handler_instance.family_tree.members[molly_id]
    assert not molly_updated.nicknames
    assert not molly_updated.HasField("date_of_birth")

    molly_node = handler.graph_handler_instance.nx_graph.nodes[molly_id]
    assert "Nicknames" not in molly_node["title"]
    assert "Date Of Birth" not in molly_node["title"]


def test_update_member_not_found(weasley_handler):
    """Test updating a member ID that doesn't exist."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()

    update_data = {"name": "Non Existent"}
    with pytest.raises(Exception) as excinfo:
        handler.update_member("GHOSTID", update_data)
    assert "Cannot update: Member with ID 'GHOSTID' not found." in str(excinfo.value)
    assert len(handler.proto_handler_instance.family_tree.members) == 9


def test_update_member_invalid_data(weasley_handler):
    """Test updating with data that fails validation (e.g., DoD < DoB)."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    fred_id = "FREDW"

    update_data = {
        "name": "Fred Weasley",
        "gender": "MALE",
        "IsAlive": False,
        "dob_date": 1,
        "dob_month": 4,
        "dob_year": 1978,
        "dod_date": 1,
        "dod_month": 1,
        "dod_year": 1970,  # Invalid DoD year
    }
    with pytest.raises(Exception) as excinfo:
        handler.update_member(fred_id, update_data)
    assert "Date of Death cannot be before Date of Birth" in str(excinfo.value)

    fred_original = handler.proto_handler_instance.family_tree.members[fred_id]
    assert fred_original.date_of_death.year == 1998


def test_display_family_tree_success(weasley_handler):
    """Test generating the HTML output file."""
    handler, _, output_html_file, _ = weasley_handler
    handler.load_from_text_file()
    # Tell the handler where to save the file for this test ---
    handler.graph_handler_instance.update_output_html_file(output_html_file)
    handler.display_tree()
    assert os.path.exists(output_html_file)
    assert os.path.getsize(output_html_file) > 500


def test_display_family_tree_empty_graph(tmp_path):
    """Test generating HTML when the graph is empty."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    output_file = handler.graph_handler_instance.output_html_file
    handler.display_tree()
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "No family tree data loaded." in content


@patch("os.makedirs")
def test_display_family_tree_dir_error(mock_makedirs, tmp_path):
    """Test display_family_tree when output directory creation fails."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    mock_makedirs.side_effect = OSError("Permission denied")
    handler.graph_handler_instance.output_html_file = str(
        tmp_path / "uncreatable_dir" / "tree.html"
    )

    with pytest.raises(IOError) as excinfo:
        handler.display_tree()
    assert "Cannot create output directory" in str(excinfo.value)
    assert "Permission denied" in str(excinfo.value.__cause__)


def test_save_to_protobuf_success(weasley_handler):
    """Test saving the current family tree state to a .txtpb file."""
    handler, _, _, output_data_file = weasley_handler
    handler.load_from_text_file()
    handler.create_member({"name": "Harry Potter", "gender": "MALE"})
    # Tell the handler where to save the file for this test ---
    handler.proto_handler_instance.update_output_data_file(output_data_file)
    handler.save_to_text_file()
    assert os.path.exists(output_data_file)

    saved_tree = family_tree_pb2.FamilyTree()
    with open(output_data_file, "r", encoding="utf-8") as f:
        text_format.Merge(f.read(), saved_tree)

    assert len(saved_tree.members) == 10
    assert "ARTHW" in saved_tree.members
    assert any(m.name == "Harry Potter" for m in saved_tree.members.values())


@patch("google.protobuf.text_format.MessageToString")
def test_save_to_protobuf_error(mock_msg_to_string, tmp_path):
    """Test error handling during protobuf saving."""
    handler = FamilyTreeHandler(
        temp_dir_path=str(tmp_path)
    )  # output_data_file will be default
    handler.create_member({"name": "Test Member"})
    mock_msg_to_string.side_effect = TypeError("Serialization failed")
    with pytest.raises(Exception) as excinfo:
        handler.save_to_text_file()
    assert "An unexpected error occurred during saving" in str(excinfo.value)
    assert "Serialization failed" in str(excinfo.value.__cause__)


def test_update_data_source(tmp_path):
    """Test updating the input file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_source.txtpb"
    handler.update_data_source(str(new_path))
    assert handler.proto_handler_instance.input_text_file == str(new_path)


def test_update_output_html_file(tmp_path):
    """Test updating the output HTML file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_output.html"
    handler.update_output_html_file(str(new_path))
    assert handler.graph_handler_instance.output_html_file == str(new_path)


def test_update_output_data_file(tmp_path):
    """Test updating the output protobuf data file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_data_export.txtpb"
    handler.update_output_data_file(str(new_path))
    assert handler.proto_handler_instance.output_proto_data_file == str(new_path)


def test_load_populates_graph_warnings(weasley_handler, caplog):
    """Test warnings during graph population (e.g., missing spouse/child)."""
    handler, _, _, _ = weasley_handler
    # Load initial valid data
    handler.load_from_text_file()
    caplog.set_level(logging.WARNING)

    # Test missing spouse
    handler.proto_handler_instance.family_tree.relationships["ARTHW"].spouse_ids.append(
        "GHOSTSPOUSE"
    )
    handler.graph_handler_instance.nx_graph.clear()  # Clear graph before re-populating
    handler._add_familytree_members_to_graph()  # Call the internal method directly for this specific test
    assert (
        "Spouse ID GHOSTSPOUSE not found for member ARTHW. Skipping edge."
        in caplog.text
    )
    handler.proto_handler_instance.family_tree.relationships["ARTHW"].spouse_ids.remove(
        "GHOSTSPOUSE"
    )
    caplog.clear()

    # Test missing child
    handler.proto_handler_instance.family_tree.relationships[
        "MOLLW"
    ].children_ids.append("GHOSTCHILD")
    handler.graph_handler_instance.nx_graph.clear()
    handler._add_familytree_members_to_graph()
    assert (
        "Child ID GHOSTCHILD not found for parent MOLLW. Skipping edge." in caplog.text
    )
    handler.proto_handler_instance.family_tree.relationships[
        "MOLLW"
    ].children_ids.remove("GHOSTCHILD")
    caplog.clear()

    # Test ID mismatch
    original_id = handler.proto_handler_instance.family_tree.members["RONAW"].id
    handler.proto_handler_instance.family_tree.members[
        "RONAW"
    ].id = "DIFFERENTID"  # Create mismatch
    handler.graph_handler_instance.nx_graph.clear()
    handler._add_familytree_members_to_graph()
    assert "Mismatch between map key 'RONAW' and member.id 'DIFFERENTID'" in caplog.text
    assert "DIFFERENTID" in handler.graph_handler_instance.nx_graph.nodes
    # The original key "RONAW" might still exist if the member object under that key was not updated,
    # but the node added to the graph should use "DIFFERENTID".
    # Depending on implementation, "RONAW" might or might not be in the graph if its member.id changed.
    # The current implementation of _add_familytree_members_to_graph uses member.id for the graph.
    assert "RONAW" not in handler.graph_handler_instance.nx_graph.nodes
    handler.proto_handler_instance.family_tree.members[
        "RONAW"
    ].id = original_id  # Restore


def test_clear_method(weasley_handler):
    """Test the clear method."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    assert len(handler.proto_handler_instance.family_tree.members) > 0
    assert len(handler.graph_handler_instance.nx_graph.nodes) > 0

    handler.clear()
    assert len(handler.proto_handler_instance.family_tree.members) == 0
    assert len(handler.graph_handler_instance.nx_graph.nodes) == 0


def test_query_member_pass_through(weasley_handler):
    """Test the query_member pass-through method."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    member = handler.query_member("ARTHW")
    assert member is not None
    assert member.name == "Arthur Weasley"
    assert handler.query_member("NOSUCHID") is None


def test_get_members_pass_through(weasley_handler):
    """Test the get_members pass-through method."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    members = list(handler.get_members())
    assert len(members) == 9
    assert any(m.name == "Ginny Weasley" for m in members)


def test_get_member_ids_pass_through(weasley_handler):
    """Test the get_member_ids pass-through method."""
    handler, _, _, _ = weasley_handler
    handler.load_from_text_file()
    member_ids = list(handler.get_member_ids())
    assert len(member_ids) == 9
    assert "ARTHW" in member_ids
    assert "GINNW" in member_ids
