import logging
import os
from unittest.mock import patch

import google.protobuf.text_format as text_format
import pytest

# Assuming protos are generated and accessible relative to the tests directory
# Adjust the import path if your structure is different
import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.family_tree_handler import COLOR_PALETTLE, FamilyTreeHandler

# --- Test Data Generation ---


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

    # FIXME: Currently, there is no parent ID
    ## Children's relationships (only parents for simplicity here)
    ## In a real scenario, you might add spouses/children for them too
    # for child_id in ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]:
    # child_rel = family_tree.relationships[child_id]
    # child_rel.parent_ids.extend(
    # ["ARTHW", "MOLLW"]
    # )  # Assuming parent_ids field exists

    return family_tree


# --- Fixture ---
@pytest.fixture
def weasley_handler(tmp_path):
    """Fixture to create a FamilyTreeHandler instance with Weasley data."""
    # Create a temporary directory for this test run provided by pytest
    test_dir = tmp_path / "family_data"
    test_dir.mkdir()

    # Define file paths within the temporary directory
    input_file = test_dir / "weasley_family.txtpb"
    output_html_file = test_dir / "weasley_tree.html"
    output_data_file = test_dir / "weasley_data_export.txtpb"

    # Create the test data file
    weasley_tree_proto = create_weasley_family_tree_proto()
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(text_format.MessageToString(weasley_tree_proto, as_utf8=True))

    # Instantiate the handler, passing the temporary directory path
    handler = FamilyTreeHandler(
        temp_dir_path=str(test_dir),  # Pass the main temp dir
        input_file=str(input_file),
        # Let handler use default output paths initially based on temp_dir_path
        # output_file=str(output_html_file),
        # output_data_file=str(output_data_file)
    )

    # Yield handler and paths for use in tests
    yield handler, str(input_file), str(output_html_file), str(output_data_file)

    # No explicit cleanup needed, tmp_path handles directory removal


# --- Test Functions ---


def test_init_defaults(tmp_path):
    """Test if handler initializes with correct default output paths."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    assert handler.input_file is None
    assert handler.output_file == os.path.join(tmp_path, "family_tree.html")
    assert handler.output_proto_data_file == os.path.join(
        tmp_path, "family_tree_data.txtpb"
    )
    assert not handler.family_tree.members  # Should be empty initially
    assert not handler.nx_graph.nodes  # Should be empty initially


def test_load_from_protobuf_success(weasley_handler, caplog):
    """Test successful loading of the Weasley protobuf data."""
    handler, input_file, _, _ = weasley_handler
    # Explicitly set the capture level for this test
    caplog.set_level(logging.INFO)
    handler.load_from_protobuf()

    assert len(handler.family_tree.members) == 9  # Arthur, Molly + 7 children
    assert (
        len(handler.family_tree.relationships) >= 2
    )  # Arthur, Molly + children potentially
    assert "ARTHW" in handler.family_tree.members
    assert handler.family_tree.members["ARTHW"].name == "Arthur Weasley"
    assert "GINNW" in handler.family_tree.members
    assert handler.family_tree.members["GINNW"].gender == utils_pb2.FEMALE
    expected_string = f"Successfully loaded {input_file}"
    # Read captured stdout
    stdout_output = caplog.text
    assert expected_string in stdout_output


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


def test_populate_nodes_and_edges(weasley_handler):
    """Test population of the NetworkX graph from loaded protobuf."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()  # This calls populate_nodes_and_edges internally

    # Check nodes
    assert len(handler.nx_graph.nodes) == 9
    assert "ARTHW" in handler.nx_graph.nodes
    assert "MOLLW" in handler.nx_graph.nodes
    assert "RONAW" in handler.nx_graph.nodes
    assert handler.nx_graph.nodes["ARTHW"]["label"] == "Arthur Weasley"
    assert handler.nx_graph.nodes["GINNW"]["label"] == "Ginny Weasley"

    # Check edges (Spouse + Children)
    # Arthur -> Molly (Spouse) & Molly -> Arthur (Spouse)
    # Arthur -> Child (x7)
    # Molly -> Child (x7)
    expected_edge_count = 2 + 7 + 7
    assert len(handler.nx_graph.edges) == expected_edge_count

    # Check specific edges and properties
    assert handler.nx_graph.has_edge("ARTHW", "MOLLW")
    assert handler.nx_graph.edges["ARTHW", "MOLLW"]["color"] == COLOR_PALETTLE["pink"]
    assert handler.nx_graph.has_edge("MOLLW", "ARTHW")
    assert handler.nx_graph.edges["MOLLW", "ARTHW"]["color"] == COLOR_PALETTLE["pink"]

    assert handler.nx_graph.has_edge("ARTHW", "RONAW")
    assert handler.nx_graph.edges["ARTHW", "RONAW"]["weight"] == 1  # Child edge weight
    assert handler.nx_graph.has_edge("MOLLW", "FREDW")
    assert handler.nx_graph.edges["MOLLW", "FREDW"]["weight"] == 1

    # Check a node's properties (e.g., Ginny)
    ginny_node = handler.nx_graph.nodes["GINNW"]
    assert ginny_node["label"] == "Ginny Weasley"
    assert (
        ginny_node["shape"] == "circularImage"
    )  # Assuming default images are found/mocked
    assert "image" in ginny_node  # Check key exists
    assert "title" in ginny_node  # Check tooltip key exists
    assert "Ginny Weasley" in ginny_node["title"]
    assert "FEMALE" in ginny_node["title"]
    assert "CHITHIRAI" in ginny_node["title"]  # Check traditional date in tooltip


def test_add_node_from_proto_object_image_logic(tmp_path):
    """Test node shape and image based on image availability."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    # Mock default images
    mock_return_value = (
        {"MALE": "/path/to/male.png", "FEMALE": "/path/to/female.png"},
        "/path/to/broken.gif",
    )

    # Use patch.object as a context manager
    # Patch the 'get_default_images' method directly on the FamilyTreeHandler class
    with patch.object(
        FamilyTreeHandler, "get_default_images", return_value=mock_return_value
    ) as mock_method:
        # --- Test Cases within the 'with' block ---

        # Case 1: No image_location provided, use default
        harry = family_tree_pb2.FamilyMember(
            id="HARRP", name="Harry Potter", gender=utils_pb2.MALE
        )
        handler.add_node_from_proto_object(harry)  # Call happens while patch is active
        assert handler.nx_graph.nodes["HARRP"]["shape"] == "circularImage"
        # This assertion should now pass because the mock is guaranteed to be called
        assert handler.nx_graph.nodes["HARRP"]["image"] == "/path/to/male.png"
        assert handler.nx_graph.nodes["HARRP"]["brokenImage"] == "/path/to/broken.gif"
        # You can optionally assert the mock was called if needed
        mock_method.assert_called_once()
        mock_method.reset_mock()  # Reset call count for the next case

        # Case 2: image_location provided and exists (mock os.path.exists)
        hermione = family_tree_pb2.FamilyMember(
            id="HERMG", name="Hermione Granger", gender=utils_pb2.FEMALE
        )
        hermione.additional_info["image_location"] = "/valid/path/hermione.jpg"
        # Patch os.path.exists specifically for this case
        with patch("os.path.exists", return_value=True) as mock_exists:
            handler.add_node_from_proto_object(hermione)
            mock_exists.assert_called_with("/valid/path/hermione.jpg")
        assert handler.nx_graph.nodes["HERMG"]["shape"] == "circularImage"
        assert handler.nx_graph.nodes["HERMG"]["image"] == "/valid/path/hermione.jpg"
        # Assert get_default_images was still called (even if its result wasn't used for the final path)
        mock_method.assert_called_once()
        mock_method.reset_mock()

        # Case 3: image_location provided but doesn't exist (mock os.path.exists)
        luna = family_tree_pb2.FamilyMember(
            id="LUNAL", name="Luna Lovegood", gender=utils_pb2.FEMALE
        )
        luna.additional_info["image_location"] = "/invalid/path/luna.png"
        with patch("os.path.exists", return_value=False) as mock_exists:
            handler.add_node_from_proto_object(luna)
            mock_exists.assert_called_with("/invalid/path/luna.png")
        # Should fall back to default female image from the mock
        assert handler.nx_graph.nodes["LUNAL"]["shape"] == "circularImage"
        assert (
            handler.nx_graph.nodes["LUNAL"]["image"] == "/path/to/female.png"
        )  # Uses mock return value
        mock_method.assert_called_once()
        mock_method.reset_mock()

    # --- Test Case 4 needs a different mock return value ---
    # Create a new handler instance or re-patch with different value outside the first 'with' block
    handler_no_defaults = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    mock_return_no_defaults = ({}, "/path/to/broken.gif")  # No defaults

    with patch.object(
        FamilyTreeHandler, "get_default_images", return_value=mock_return_no_defaults
    ) as mock_method_no_defaults:
        # Case 4: No image_location, no default image found
        dobby = family_tree_pb2.FamilyMember(
            id="DOBBY", name="Dobby", gender=utils_pb2.OTHER
        )
        handler_no_defaults.add_node_from_proto_object(dobby)
        assert (
            handler_no_defaults.nx_graph.nodes["DOBBY"]["shape"] == "dot"
        )  # Fallback shape
        assert handler_no_defaults.nx_graph.nodes["DOBBY"]["image"] is None
        mock_method_no_defaults.assert_called_once()


def test_generate_member_id(tmp_path):
    """Test generation of unique member IDs."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    id1 = handler.generate_member_id()
    id2 = handler.generate_member_id()
    assert isinstance(id1, str)
    assert len(id1) == 4
    assert id1 != id2  # Highly likely, though not guaranteed without mocking random
    assert id1.isalnum() and id1.isupper()  # Check format (uppercase letters + digits)


def test_create_node_basic(tmp_path, caplog):
    """Test creating a basic node with minimal info."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    # Explicitly set the capture level for this test
    caplog.set_level(logging.INFO)
    input_data = {"name": "Sirius Black", "gender": "MALE", "IsAlive": False}
    handler.create_node(input_data)
    assert len(handler.family_tree.members) == 1
    member_id = list(handler.family_tree.members.keys())[0]  # Get the generated ID
    assert len(member_id) == 4
    sirius = handler.family_tree.members[member_id]
    assert sirius.id == member_id
    assert sirius.name == "Sirius Black"
    assert sirius.gender == utils_pb2.MALE
    assert not sirius.alive
    assert sirius.date_of_birth.year == 0  # Not provided
    assert sirius.date_of_death.year == 0  # Not provided

    assert len(handler.nx_graph.nodes) == 1
    assert member_id in handler.nx_graph.nodes
    assert handler.nx_graph.nodes[member_id]["label"] == "Sirius Black"
    assert f"Created node with ID: {member_id}, Name: Sirius Black" in caplog.text


def test_create_node_full(tmp_path):
    """Test creating a node with more complete information."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    input_data = {
        "name": "Remus Lupin",
        "nicknames": "Moony",
        "gender": "MALE",
        "dob_date": 10,
        "dob_month": 3,
        "dob_year": 1960,  # Provide DOB fields
        "dob_traditional_month": "PANGUNI",
        "dob_traditional_star": "PUNARPOOSAM",
        "IsAlive": False,
        "dod_date": 2,
        "dod_month": 5,
        "dod_year": 1998,  # Provide DOD fields
        "dod_traditional_month": "VAIKASI",
        "dod_traditional_paksham": "KRISHNA",
        "dod_traditional_thithi": "DWITHIYAI",
    }
    handler.create_node(input_data)
    member_id = list(handler.family_tree.members.keys())[0]
    lupin = handler.family_tree.members[member_id]

    assert lupin.name == "Remus Lupin"
    assert list(lupin.nicknames) == ["Moony"]
    assert lupin.gender == utils_pb2.MALE
    assert lupin.date_of_birth.year == 1960
    assert lupin.date_of_birth.month == 3
    assert lupin.date_of_birth.date == 10
    assert lupin.traditional_date_of_birth.month == utils_pb2.PANGUNI
    assert lupin.traditional_date_of_birth.star == utils_pb2.PUNARPOOSAM
    assert not lupin.alive
    assert lupin.date_of_death.year == 1998
    assert lupin.date_of_death.month == 5
    assert lupin.date_of_death.date == 2
    assert lupin.traditional_date_of_death.month == utils_pb2.VAIKASI
    assert lupin.traditional_date_of_death.paksham == utils_pb2.KRISHNA
    assert lupin.traditional_date_of_death.thithi == utils_pb2.DWITHIYAI


def test_create_node_invalid_input(tmp_path, caplog):
    """Test node creation with invalid data (e.g., empty name, bad enum)."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))

    # Empty name
    member_id, message = handler.create_node({"name": "  ", "gender": "MALE"})
    # print(f"Member_id: {member_id}, Message: {message}")
    assert len(handler.family_tree.members) == 0  # Should not create
    assert "Cannot create node: Name cannot be empty." in message

    # Invalid gender
    member_id, message = handler.create_node(
        {"name": "Nymphadora Tonks", "gender": "METAMORPHMAGUS"}
    )
    # print(f"Member_id: {member_id}, Message: {message}")
    assert len(handler.family_tree.members) == 1
    member_id = list(handler.family_tree.members.keys())[0]
    tonks = handler.family_tree.members[member_id]
    assert tonks.gender == utils_pb2.GENDER_UNKNOWN  # Should default
    assert "Invalid gender value 'METAMORPHMAGUS'" in caplog.text

    # Invalid date parts
    member_id, message = handler.create_node(
        {"name": "Albus Dumbledore", "gender": "MALE", "dob_date": 40}
    )
    # print(f"Member_id: {member_id}, Message: {message}")
    assert (
        len(handler.family_tree.members) == 1
    )  # As date validation should have failed
    assert "Incomplete Gregorian date provided" in message


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
    assert "Nicknames: ['Half-Blood Prince']" in title  # Check list format
    assert "Gender: MALE" in title
    assert "Alive: False" in title
    assert (
        "Date Of Birth: {'year': 1960, 'month': 1, 'date': 9}" in title
    )  # Check dict format
    assert "Date Of Death: {'year': 1998, 'month': 5, 'date': 2}" in title
    # Check that empty fields are not present
    assert "Traditional Date Of Birth" not in title


def test_display_family_tree_success(weasley_handler):
    """Test generating the HTML output file."""
    handler, _, _, _ = weasley_handler
    # Use the default output path calculated by __init__
    default_output_html = handler.output_file
    handler.load_from_protobuf()
    handler.display_family_tree()
    assert os.path.exists(default_output_html)
    # Check if file has substantial content (more than just empty html tags)
    assert os.path.getsize(default_output_html) > 500


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
    # Make makedirs raise an error
    mock_makedirs.side_effect = OSError("Permission denied")
    handler.output_file = tmp_path / "uncreatable_dir" / "tree.html"

    with pytest.raises(IOError) as excinfo:
        handler.display_family_tree()
    assert "Cannot create output directory" in str(excinfo.value)
    assert "Permission denied" in str(excinfo.value.__cause__)


def test_save_to_protobuf_success(weasley_handler):
    """Test saving the current family tree state to a .txtpb file."""
    handler, _, _, _ = weasley_handler
    default_output_data = handler.output_proto_data_file
    handler.load_from_protobuf()
    # Add a new member to test saving the modified state
    handler.create_node({"name": "Harry Potter", "gender": "MALE"})

    handler.save_to_protobuf()
    assert os.path.exists(default_output_data)

    # Read back and verify content
    saved_tree = family_tree_pb2.FamilyTree()
    with open(default_output_data, "r", encoding="utf-8") as f:
        text_format.Merge(f.read(), saved_tree)

    assert len(saved_tree.members) == 10  # Original 9 + Harry
    assert "ARTHW" in saved_tree.members
    assert any(m.name == "Harry Potter" for m in saved_tree.members.values())


@patch("google.protobuf.text_format.MessageToString")
def test_save_to_protobuf_error(mock_msg_to_string, tmp_path):
    """Test error handling during protobuf saving."""
    handler = FamilyTreeHandler(temp_dir_path=str(tmp_path))
    handler.create_node({"name": "Test Member"})  # Add some data
    mock_msg_to_string.side_effect = TypeError("Serialization failed")

    with pytest.raises(Exception) as excinfo:  # Catch the re-raised exception
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
    assert "OTHER" in genders
    assert "GENDER_UNKNOWN" in genders

    months = handler.get_enum_values_from_proto_schema("TamilMonth")
    assert "CHITHIRAI" in months
    assert "VAIKASI" in months
    assert "TAMIL_MONTH_UNKNOWN" in months

    invalid = handler.get_enum_values_from_proto_schema("NonExistentEnum")
    assert invalid == []

    invalid_module = handler.get_enum_values_from_proto_schema(
        "Gender", proto_module=os
    )  # Wrong module
    assert invalid_module == []


def test_populate_nodes_and_edges_warnings(weasley_handler, caplog):
    """Test warnings during graph population (e.g., missing spouse/child)."""
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()  # Load initial data

    # --- Test missing spouse ---
    # Add a relationship pointing to a non-existent spouse
    handler.family_tree.relationships["ARTHW"].spouse_ids.append("GHOSTSPOUSE")
    # Clear and repopulate graph to trigger edge creation again
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert (
        "Spouse ID GHOSTSPOUSE not found for member ARTHW. Skipping edge."
        in caplog.text
    )
    # Ensure the bad edge wasn't added
    assert not handler.nx_graph.has_edge("ARTHW", "GHOSTSPOUSE")
    # Reset for next test
    handler.family_tree.relationships["ARTHW"].spouse_ids.remove("GHOSTSPOUSE")
    caplog.clear()

    # --- Test missing child ---
    handler.family_tree.relationships["MOLLW"].children_ids.append("GHOSTCHILD")
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert (
        "Child ID GHOSTCHILD not found for parent MOLLW. Skipping edge." in caplog.text
    )
    assert not handler.nx_graph.has_edge("MOLLW", "GHOSTCHILD")
    # Reset
    handler.family_tree.relationships["MOLLW"].children_ids.remove("GHOSTCHILD")
    caplog.clear()

    # --- Test ID mismatch ---
    # Modify a member's ID after it's in the map key
    original_id = handler.family_tree.members["RONAW"].id
    handler.family_tree.members["RONAW"].id = "DIFFERENTID"
    handler.nx_graph.clear()
    handler.populate_nodes_and_edges()
    assert "Mismatch between map key 'RONAW' and member.id 'DIFFERENTID'" in caplog.text
    # Ensure node was added with the correct ID from the member object
    assert "DIFFERENTID" in handler.nx_graph.nodes
    assert (
        "RONAW" not in handler.nx_graph.nodes
    )  # Original key shouldn't be used as node ID
    # Reset
    handler.family_tree.members["RONAW"].id = original_id  # Put it back for other tests


# Example of how you might test print_member_details if needed (using capsys)
def test_print_member_details(weasley_handler, capsys):
    handler, _, _, _ = weasley_handler
    handler.load_from_protobuf()
    handler.print_member_details("MOLLW")
    captured = capsys.readouterr()
    captured_text = captured.out
    assert 'id: "MOLLW"' in captured_text
    assert 'name: "Molly Weasley"' in captured_text
    assert 'nicknames: "Mollywobbles"' in captured_text
    assert "gender: FEMALE" in captured_text  # Check enum name is printed
