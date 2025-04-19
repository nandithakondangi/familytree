import logging
import os
from unittest.mock import patch

import google.protobuf.text_format as text_format
import pytest

# Assuming protos are generated and accessible relative to the tests directory
# Adjust the import path if your structure is different
import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.family_tree_handler import (
    COLOR_PALETTLE,
    FamilyTreeHandler,
)

# --- Test Data Generation (create_weasley_family_tree_proto remains the same) ---


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
    # Add traditional date example
    ginny.traditional_date_of_birth.month = utils_pb2.CHITHIRAI
    ginny.traditional_date_of_birth.star = utils_pb2.ASHWINI

    # --- Relationships ---
    # Arthur's relationships
    arthur_rel = family_tree.relationships["ARTHW"]
    arthur_rel.spouse_ids.append("MOLLW")
    arthur_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    # Molly's relationships
    molly_rel = family_tree.relationships["MOLLW"]
    molly_rel.spouse_ids.append("ARTHW")
    molly_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    return family_tree


# --- Fixture (weasley_handler remains the same) ---
@pytest.fixture
def weasley_handler(tmp_path):
    """Fixture to create a FamilyTreeHandler instance with Weasley data."""
    test_dir = tmp_path / "family_data"
    test_dir.mkdir()
    input_file = test_dir / "weasley_family.txtpb"
    output_html_file = test_dir / "weasley_tree.html"  # Default path
    output_data_file = test_dir / "weasley_data_export.txtpb"  # Default path

    weasley_tree_proto = create_weasley_family_tree_proto()
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(text_format.MessageToString(weasley_tree_proto, as_utf8=True))

    handler = FamilyTreeHandler(temp_dir_path=str(test_dir), input_file=str(input_file))
    # Yield handler and expected default paths for verification
    yield handler, str(input_file), str(output_html_file), str(output_data_file)


# --- Test Functions ---

# --- Initialization and Loading Tests (mostly unchanged) ---


def test_init_defaults(tmp_path):
    """Test if handler initializes with correct default output paths."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    assert handler.input_file is None
    assert handler.output_file == os.path.join(tmp_path, "family_tree.html")
    assert handler.output_proto_data_file == os.path.join(
        tmp_path, "family_tree_data.txtpb"
    )
    assert not handler.family_tree.members
    assert not handler.nx_graph.nodes


def test_load_from_protobuf_success(weasley_handler, caplog):
    """Test successful loading of the Weasley protobuf data."""
    handler, input_file, _, _ = weasley_handler
    caplog.set_level(logging.INFO)
    handler.load_from_protobuf()

    assert len(handler.family_tree.members) == 9
    assert len(handler.family_tree.relationships) >= 2
    assert "ARTHW" in handler.family_tree.members
    assert handler.family_tree.members["ARTHW"].name == "Arthur Weasley"
    assert "GINNW" in handler.family_tree.members
    assert handler.family_tree.members["GINNW"].gender == utils_pb2.FEMALE
    assert f"Successfully loaded {input_file}" in caplog.text


def test_load_from_protobuf_file_not_found(tmp_path):
    """Test loading when the input file does not exist."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    non_existent_file = tmp_path / "ghost_file.txtpb"
    handler.update_data_source(str(non_existent_file))

    with pytest.raises(FileNotFoundError) as excinfo:
        handler.load_from_protobuf()
    assert str(non_existent_file) in str(excinfo.value)


def test_load_from_protobuf_parse_error(tmp_path, caplog):
    """Test loading a file with invalid protobuf format."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    bad_file = tmp_path / "bad_format.txtpb"
    with open(bad_file, "w") as f:
        f.write("this is not protobuf text format {")

    handler.update_data_source(str(bad_file))
    with pytest.raises(text_format.ParseError):
        handler.load_from_protobuf()
    assert f"Error parsing protobuf text file {bad_file}" in caplog.text


# --- Graph Population Tests (mostly unchanged) ---


def test_populate_nodes_and_edges(weasley_handler):
    """Test population of the NetworkX graph from loaded protobuf."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()

    assert len(handler.nx_graph.nodes) == 9
    assert "ARTHW" in handler.nx_graph.nodes
    assert handler.nx_graph.nodes["ARTHW"]["label"] == "Arthur Weasley"
    assert handler.nx_graph.has_edge("ARTHW", "MOLLW")
    assert handler.nx_graph.edges["ARTHW", "MOLLW"]["color"] == COLOR_PALETTLE["pink"]
    assert handler.nx_graph.has_edge("ARTHW", "RONAW")
    assert handler.nx_graph.edges["ARTHW", "RONAW"]["weight"] == 1

    ginny_node = handler.nx_graph.nodes["GINNW"]
    assert ginny_node["label"] == "Ginny Weasley"
    assert "title" in ginny_node
    assert "Ginny Weasley" in ginny_node["title"]
    assert "FEMALE" in ginny_node["title"]
    assert "CHITHIRAI" in ginny_node["title"]


def test_add_or_update_node_from_proto_object_image_logic(tmp_path):
    """Test node shape and image based on image availability."""
    # This test focuses on add_or_update_node_from_proto_object, which wasn't refactored
    # It remains valid.
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    mock_return_value = (
        {"MALE": "/path/to/male.png", "FEMALE": "/path/to/female.png"},
        "/path/to/broken.gif",
    )

    with patch.object(
        FamilyTreeHandler, "get_default_images", return_value=mock_return_value
    ) as mock_method:
        # Case 1: No image_location, use default
        harry = family_tree_pb2.FamilyMember(
            id="HARRP", name="Harry Potter", gender=utils_pb2.MALE
        )
        handler.add_or_update_node_from_proto_object(harry)
        assert handler.nx_graph.nodes["HARRP"]["shape"] == "circularImage"
        assert handler.nx_graph.nodes["HARRP"]["image"] == "/path/to/male.png"
        mock_method.assert_called_once()
        mock_method.reset_mock()

        # Case 2: image_location provided and exists
        hermione = family_tree_pb2.FamilyMember(
            id="HERMG", name="Hermione Granger", gender=utils_pb2.FEMALE
        )
        hermione.additional_info["image_location"] = "/valid/path/hermione.jpg"
        with patch("os.path.exists", return_value=True) as mock_exists:
            handler.add_or_update_node_from_proto_object(hermione)
            mock_exists.assert_called_with("/valid/path/hermione.jpg")
        assert handler.nx_graph.nodes["HERMG"]["shape"] == "circularImage"
        assert handler.nx_graph.nodes["HERMG"]["image"] == "/valid/path/hermione.jpg"
        mock_method.assert_called_once()
        mock_method.reset_mock()

        # Case 3: image_location provided but doesn't exist
        luna = family_tree_pb2.FamilyMember(
            id="LUNAL", name="Luna Lovegood", gender=utils_pb2.FEMALE
        )
        luna.additional_info["image_location"] = "/invalid/path/luna.png"
        with patch("os.path.exists", return_value=False) as mock_exists:
            handler.add_or_update_node_from_proto_object(luna)
            mock_exists.assert_called_with("/invalid/path/luna.png")
        assert handler.nx_graph.nodes["LUNAL"]["shape"] == "circularImage"
        assert handler.nx_graph.nodes["LUNAL"]["image"] == "/path/to/female.png"
        mock_method.assert_called_once()

    # Case 4: No image_location, no default image found
    handler_no_defaults = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    mock_return_no_defaults = ({}, "/path/to/broken.gif")
    with patch.object(
        FamilyTreeHandler, "get_default_images", return_value=mock_return_no_defaults
    ) as mock_method_no_defaults:
        dobby = family_tree_pb2.FamilyMember(
            id="DOBBY", name="Dobby", gender=utils_pb2.OTHER
        )
        handler_no_defaults.add_or_update_node_from_proto_object(dobby)
        assert handler_no_defaults.nx_graph.nodes["DOBBY"]["shape"] == "dot"
        assert handler_no_defaults.nx_graph.nodes["DOBBY"]["image"] is None
        mock_method_no_defaults.assert_called_once()


# --- Node Creation Tests (verify existing tests) ---


def test_create_node_basic(tmp_path, caplog):
    """Test creating a basic node with minimal info."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    caplog.set_level(logging.INFO)
    input_data = {"name": "Sirius Black", "gender": "MALE", "IsAlive": False}
    member_id, error_msg = handler.create_node(input_data)

    assert error_msg is None
    assert member_id is not None
    assert len(member_id) == 4
    assert len(handler.family_tree.members) == 1
    assert member_id in handler.family_tree.members

    sirius = handler.family_tree.members[member_id]
    assert sirius.id == member_id
    assert sirius.name == "Sirius Black"
    assert sirius.gender == utils_pb2.MALE
    assert not sirius.alive

    assert len(handler.nx_graph.nodes) == 1
    assert member_id in handler.nx_graph.nodes
    assert handler.nx_graph.nodes[member_id]["label"] == "Sirius Black"
    # Check the log message from _add_member_to_tree_and_graph
    assert (
        f"Successfully added/updated member {member_id} ('Sirius Black') in tree and graph."
        in caplog.text
    )


def test_create_node_full(tmp_path):
    """Test creating a node with more complete information."""
    # This test checks the final state, which should be unchanged by the refactor.
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
    member_id, error_msg = handler.create_node(input_data)

    assert error_msg is None
    assert member_id is not None
    assert len(handler.family_tree.members) == 1
    lupin = handler.family_tree.members[member_id]

    assert lupin.name == "Remus Lupin"
    assert list(lupin.nicknames) == ["Moony"]
    assert lupin.gender == utils_pb2.MALE
    assert lupin.date_of_birth.year == 1960
    assert lupin.traditional_date_of_birth.month == utils_pb2.PANGUNI
    assert not lupin.alive
    assert lupin.date_of_death.year == 1998
    assert lupin.traditional_date_of_death.paksham == utils_pb2.KRISHNA

    assert member_id in handler.nx_graph.nodes
    assert handler.nx_graph.nodes[member_id]["label"] == "Remus Lupin"


def test_create_node_invalid_input(tmp_path, caplog):
    """Test node creation with invalid data (e.g., empty name, bad enum, bad date)."""
    # This test checks the error handling, which should be unchanged externally.
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    caplog.set_level(logging.WARNING)  # Capture warnings for invalid gender

    # Empty name
    member_id, message = handler.create_node({"name": "  ", "gender": "MALE"})
    assert member_id is None
    assert "Validation Error: Name cannot be empty." in message
    assert len(handler.family_tree.members) == 0  # Should not create

    # Invalid gender (should still create but log warning and set default)
    member_id, message = handler.create_node(
        {"name": "Nymphadora Tonks", "gender": "METAMORPHMAGUS"}
    )
    assert message is None  # Creation itself succeeds
    assert member_id is not None
    assert len(handler.family_tree.members) == 1
    tonks = handler.family_tree.members[member_id]
    assert tonks.gender == utils_pb2.GENDER_UNKNOWN  # Should default
    assert "Invalid gender value 'METAMORPHMAGUS'" in caplog.text

    # Invalid date parts (incomplete date)
    member_id, message = handler.create_node(
        {"name": "Albus Dumbledore", "gender": "MALE", "dob_date": 31}
    )
    assert member_id is None
    assert "Incomplete Gregorian date provided" in message
    assert len(handler.family_tree.members) == 1  # Only Tonks should be present

    # Invalid date value (day 31 in Feb)
    member_id, message = handler.create_node(
        {
            "name": "Gellert Grindelwald",
            "gender": "MALE",
            "dob_date": 31,
            "dob_month": 2,
            "dob_year": 1900,
        }
    )
    assert member_id is None
    assert "Date of Birth Error: Invalid day (31) for 'dob' month 2" in message
    assert len(handler.family_tree.members) == 1  # Still only Tonks


# --- Node Update Tests (NEW) ---


def test_update_node_success(weasley_handler, caplog):
    """Test successfully updating an existing node."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
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

    success, error_msg = handler.update_node(ron_id, update_data)

    assert success is True
    assert error_msg is None

    # Verify changes in protobuf
    ron_updated = handler.family_tree.members[ron_id]
    assert ron_updated.name == "Ronald Bilius Weasley"
    assert list(ron_updated.nicknames) == ["Won-Won", "Ronnie"]

    # Verify changes in graph node
    ron_node = handler.nx_graph.nodes[ron_id]
    assert ron_node["label"] == "Ronald Bilius Weasley"
    assert "Ronald Bilius Weasley" in ron_node["title"]
    assert "Won-Won" in ron_node["title"]
    assert "Ronnie" in ron_node["title"]

    assert (
        f"Successfully added/updated member {ron_id} ('Ronald Bilius Weasley') in tree and graph."
        in caplog.text
    )


def test_update_node_change_alive_status(weasley_handler):
    """Test updating alive status and adding DoD."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    george_id = "GEORW"

    # Initially George is alive
    assert handler.family_tree.members[george_id].alive is True
    assert not handler.family_tree.members[george_id].HasField("date_of_death")

    update_data = {
        "name": "George Weasley",
        "gender": "MALE",
        "IsAlive": False,  # Change status
        "dod_date": 10,
        "dod_month": 10,
        "dod_year": 2077,  # Add DoD
    }
    success, error_msg = handler.update_node(george_id, update_data)

    assert success is True
    assert error_msg is None

    george_updated = handler.family_tree.members[george_id]
    assert george_updated.alive is False
    assert george_updated.date_of_death.year == 2077
    assert george_updated.date_of_death.month == 10
    assert george_updated.date_of_death.date == 10

    # Check graph title updated
    george_node = handler.nx_graph.nodes[george_id]
    assert "Alive: False" in george_node["title"]
    assert (
        "Date Of Death: {'year': 2077, 'month': 10, 'date': 10}" in george_node["title"]
    )


def test_update_node_clear_field(weasley_handler):
    """Test that updating with empty data clears existing data."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    molly_id = "MOLLW"

    # Molly initially has a nickname
    assert "Mollywobbles" in handler.family_tree.members[molly_id].nicknames

    update_data = {
        "name": "Molly Weasley",
        "nicknames": "",  # Empty nickname string
        "gender": "FEMALE",
        "IsAlive": True,
        # No DOB provided in update
    }
    success, error_msg = handler.update_node(molly_id, update_data)

    assert success is True
    assert error_msg is None

    molly_updated = handler.family_tree.members[molly_id]
    # Nicknames should be cleared
    assert not molly_updated.nicknames
    # DOB should be cleared because it wasn't provided in the update dict
    assert not molly_updated.HasField("date_of_birth")

    # Check graph title reflects cleared fields
    molly_node = handler.nx_graph.nodes[molly_id]
    assert "Nicknames" not in molly_node["title"]
    assert "Date Of Birth" not in molly_node["title"]


def test_update_node_not_found(weasley_handler):
    """Test updating a member ID that doesn't exist."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()

    update_data = {"name": "Non Existent"}
    success, error_msg = handler.update_node("GHOSTID", update_data)

    assert success is False
    assert "Cannot update: Member with ID 'GHOSTID' not found." in error_msg
    assert len(handler.family_tree.members) == 9  # No change


def test_update_node_invalid_data(weasley_handler):
    """Test updating with data that fails validation (e.g., DoD < DoB)."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    fred_id = "FREDW"

    # Fred died in 1998, try setting DoD before DoB (1978)
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
    success, error_msg = handler.update_node(fred_id, update_data)

    assert success is False
    assert "Date of Death cannot be before Date of Birth" in error_msg

    # Verify original data wasn't changed
    fred_original = handler.family_tree.members[fred_id]
    assert fred_original.date_of_death.year == 1998


# --- _prepare_member_data Tests (Optional but Recommended) ---


def test_prepare_member_data_validation(tmp_path):
    """Directly test the validation logic in _prepare_member_data."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))

    # Valid data (new member)
    input_valid = {"name": "Valid Person", "gender": "FEMALE", "IsAlive": True}
    proto, error = handler._prepare_member_data(input_valid)
    assert error is None
    assert proto is not None
    assert proto.name == "Valid Person"
    assert proto.gender == utils_pb2.FEMALE

    # Invalid: Empty name
    input_no_name = {"name": " ", "gender": "MALE"}
    proto, error = handler._prepare_member_data(input_no_name)
    assert proto is None
    assert "Validation Error: Name cannot be empty." in error

    # Invalid: Incomplete date
    input_bad_date = {
        "name": "Bad Date Person",
        "gender": "OTHER",
        "dob_year": 2000,
    }
    proto, error = handler._prepare_member_data(input_bad_date)
    assert proto is None
    assert "Date of Birth Error: Incomplete Gregorian date provided" in error

    # Invalid: DoD < DoB
    input_dod_lt_dob = {
        "name": "Time Traveler",
        "gender": "MALE",
        "IsAlive": False,
        "dob_date": 1,
        "dob_month": 1,
        "dob_year": 2000,
        "dod_date": 1,
        "dod_month": 1,
        "dod_year": 1999,
    }
    proto, error = handler._prepare_member_data(input_dod_lt_dob)
    assert proto is None
    assert "Validation Error: Date of Death cannot be before Date of Birth." in error

    # Valid update scenario (pass existing proto)
    existing_proto = family_tree_pb2.FamilyMember(
        id="EXIST", name="Old Name", gender=utils_pb2.MALE
    )
    existing_proto.nicknames.append("OldNick")
    update_dict = {"name": "New Name", "nicknames": "NewNick", "gender": "MALE"}
    updated_proto, error = handler._prepare_member_data(
        update_dict, existing_member=existing_proto
    )
    assert error is None
    assert updated_proto is existing_proto  # Should modify in place
    assert updated_proto.name == "New Name"
    assert list(updated_proto.nicknames) == ["NewNick"]  # Old nickname replaced


# --- Other Tests (generate_node_title, display_family_tree, save_to_protobuf, etc.) ---
# These tests seem mostly unaffected by the refactor and can remain as they are.
# Verify them if issues arise.


def test_generate_member_id(tmp_path):
    """Test generation of unique member IDs."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    id1 = handler.generate_member_id()
    id2 = handler.generate_member_id()
    assert isinstance(id1, str)
    assert len(id1) == 4
    assert id1 != id2
    assert id1.isalnum() and id1.isupper()


def test_generate_node_title(tmp_path):
    """Test the generation of node tooltips."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    member = family_tree_pb2.FamilyMember(
        id="SEVS",
        name="Severus Snape",
        gender=utils_pb2.MALE,
        alive=False,
        date_of_birth=utils_pb2.GregorianDate(year=1960, month=1, date=9),
        date_of_death=utils_pb2.GregorianDate(year=1998, month=5, date=2),
    )
    member.nicknames.append("Half-Blood Prince")

    title = handler.generate_node_title(member)
    assert "Id: SEVS" in title
    assert "Name: Severus Snape" in title
    assert "Nicknames: ['Half-Blood Prince']" in title
    assert "Gender: MALE" in title
    assert "Alive: False" in title
    assert "Date Of Birth: {'year': 1960, 'month': 1, 'date': 9}" in title
    assert "Date Of Death: {'year': 1998, 'month': 5, 'date': 2}" in title
    assert "Traditional Date Of Birth" not in title


def test_display_family_tree_success(weasley_handler):
    """Test generating the HTML output file."""
    handler, _, output_html_file, _ = weasley_handler
    handler.load_from_protobuf()
    handler.display_family_tree()
    assert os.path.exists(output_html_file)
    assert os.path.getsize(output_html_file) > 500


def test_display_family_tree_empty_graph(tmp_path):
    """Test generating HTML when the graph is empty."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    output_file = handler.output_file
    handler.display_family_tree()
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "No family tree data loaded." in content


@patch("os.makedirs")
def test_display_family_tree_dir_error(mock_makedirs, tmp_path):
    """Test display_family_tree when output directory creation fails."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    mock_makedirs.side_effect = OSError("Permission denied")
    handler.output_file = tmp_path / "uncreatable_dir" / "tree.html"

    with pytest.raises(IOError) as excinfo:
        handler.display_family_tree()
    assert "Cannot create output directory" in str(excinfo.value)
    assert "Permission denied" in str(excinfo.value.__cause__)


def test_save_to_protobuf_success(weasley_handler):
    """Test saving the current family tree state to a .txtpb file."""
    handler, _, _, output_data_file = weasley_handler
    handler.load_from_protobuf()
    handler.create_node({"name": "Harry Potter", "gender": "MALE"})
    handler.save_to_protobuf()
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
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    handler.create_node({"name": "Test Member"})
    mock_msg_to_string.side_effect = TypeError("Serialization failed")

    with pytest.raises(Exception) as excinfo:
        handler.save_to_protobuf()
    assert "An unexpected error occurred during saving" in str(excinfo.value)
    assert "Serialization failed" in str(excinfo.value.__cause__)


def test_update_data_source(tmp_path):
    """Test updating the input file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_source.txtpb"
    handler.update_data_source(str(new_path))
    assert handler.input_file == str(new_path)


def test_update_output_html_file(tmp_path):
    """Test updating the output HTML file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_output.html"
    handler.update_output_html_file(str(new_path))
    assert handler.output_file == str(new_path)


def test_update_output_data_file(tmp_path):
    """Test updating the output protobuf data file path."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    new_path = tmp_path / "new_data_export.txtpb"
    handler.update_output_data_file(str(new_path))
    assert handler.output_proto_data_file == str(new_path)


def test_get_enum_values_from_proto_schema(tmp_path):
    """Test retrieving enum values."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))

    genders = handler.get_enum_values_from_proto_schema("Gender")
    assert "MALE" in genders
    assert "FEMALE" in genders

    months = handler.get_enum_values_from_proto_schema("TamilMonth")
    assert "CHITHIRAI" in months

    invalid = handler.get_enum_values_from_proto_schema("NonExistentEnum")
    assert invalid == []


def test_populate_nodes_and_edges_warnings(weasley_handler, caplog):
    """Test warnings during graph population (e.g., missing spouse/child)."""
    # This test remains valid as it tests populate_nodes_and_edges
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    caplog.set_level(logging.WARNING)

    # Test missing spouse
    handler.family_tree.relationships["ARTHW"].spouse_ids.append("GHOSTSPOUSE")
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert (
        "Spouse ID GHOSTSPOUSE not found for member ARTHW. Skipping edge."
        in caplog.text
    )
    handler.family_tree.relationships["ARTHW"].spouse_ids.remove("GHOSTSPOUSE")
    caplog.clear()

    # Test missing child
    handler.family_tree.relationships["MOLLW"].children_ids.append("GHOSTCHILD")
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert (
        "Child ID GHOSTCHILD not found for parent MOLLW. Skipping edge." in caplog.text
    )
    handler.family_tree.relationships["MOLLW"].children_ids.remove("GHOSTCHILD")
    caplog.clear()

    # Test ID mismatch
    original_id = handler.family_tree.members["RONAW"].id
    handler.family_tree.members["RONAW"].id = "DIFFERENTID"
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert "Mismatch between map key 'RONAW' and member.id 'DIFFERENTID'" in caplog.text
    assert "DIFFERENTID" in handler.nx_graph.nodes
    assert "RONAW" not in handler.nx_graph.nodes
    handler.family_tree.members["RONAW"].id = original_id


def test_print_member_details(weasley_handler, capsys):
    # This test remains valid
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    handler.print_member_details("MOLLW")
    captured = capsys.readouterr()
    captured_text = captured.out
    assert 'id: "MOLLW"' in captured_text
    assert 'name: "Molly Weasley"' in captured_text
    assert 'nicknames: "Mollywobbles"' in captured_text
    assert "gender: FEMALE" in captured_text
