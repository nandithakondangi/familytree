import os
from unittest.mock import patch

import pytest
from google.protobuf import text_format

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2
from familytree.proto_handler import ProtoHandler


# --- Test Data ---
def create_simple_member_proto(member_id="SIMP1", name="Simple Person"):
    member = family_tree_pb2.FamilyMember()
    member.id = member_id
    member.name = name
    member.gender = utils_pb2.GENDER_UNKNOWN
    member.alive = True
    return member


@pytest.fixture
def proto_handler_empty(tmp_path):
    """Provides an empty ProtoHandler instance."""
    output_file = tmp_path / "test_output.txtpb"
    return ProtoHandler(output_data_file=str(output_file))


@pytest.fixture
def proto_handler_with_data(weasley_handler):
    """Provides a ProtoHandler instance loaded with Weasley data."""
    # The weasley_handler fixture (now in conftest.py) returns a tuple:
    # (FamilyTreeHandler_instance, input_file_path, html_output_path, data_output_path)
    # We need the ProtoHandler instance from the FamilyTreeHandler instance.
    # The FamilyTreeHandler instance in weasley_handler already loads the data.
    family_tree_handler_instance, _, _, _ = weasley_handler
    # Crucially, load the data into the handler's internal protobuf object
    family_tree_handler_instance.load_from_text_file()
    return family_tree_handler_instance.proto_handler_instance


# --- ProtoHandler Tests ---


def test_load_from_protobuf(tmp_path):
    input_file = tmp_path / "test_load.txtpb"
    member = create_simple_member_proto()
    tree = family_tree_pb2.FamilyTree()
    tree.members[member.id].CopyFrom(member)
    with open(input_file, "w") as f:
        f.write(text_format.MessageToString(tree))

    handler = ProtoHandler(input_text_file=str(input_file))
    handler.load_from_protobuf()
    assert "SIMP1" in handler.family_tree.members
    assert handler.family_tree.members["SIMP1"].name == "Simple Person"


def test_save_to_protobuf(proto_handler_empty):
    handler = proto_handler_empty
    member = create_simple_member_proto("SAVE1", "Save Test")
    handler.add_member_to_proto_tree(member)
    handler.save_to_protobuf()

    assert os.path.exists(handler.output_proto_data_file)
    loaded_tree = family_tree_pb2.FamilyTree()
    with open(handler.output_proto_data_file, "r") as f:
        text_format.Merge(f.read(), loaded_tree)
    assert "SAVE1" in loaded_tree.members
    assert loaded_tree.members["SAVE1"].name == "Save Test"


def test_query_proto_member_by_id(proto_handler_with_data):
    handler = proto_handler_with_data
    arthur = handler.query_proto_member_by_id("ARTHW")
    assert arthur is not None
    assert arthur.name == "Arthur Weasley"
    assert handler.query_proto_member_by_id("NOSUCHID") is None


def test_get_family_members(proto_handler_with_data):
    handler = proto_handler_with_data
    family_members = handler.get_family_members()
    assert len(family_members) == 9  # Weasley family size
    assert any(m.name == "Ginny Weasley" for m in family_members)


def test_get_family_member_ids(proto_handler_with_data):
    handler = proto_handler_with_data
    ids = list(handler.get_family_member_ids())
    assert len(ids) == 9
    assert "MOLLW" in ids


def test_generate_member_id(proto_handler_empty):
    handler = proto_handler_empty
    id1 = handler.generate_member_id()
    id2 = handler.generate_member_id()
    assert isinstance(id1, str)
    assert len(id1) == 4
    assert id1 != id2
    assert id1.isalnum() and id1.isupper()
    # Test collision avoidance (mocking existing IDs)
    handler.family_tree.members[id1].id = id1  # Add id1 to members
    id3 = handler.generate_member_id()
    assert id3 != id1


def test_generate_new_member(proto_handler_empty):
    handler = proto_handler_empty
    new_member = handler.generate_new_member()
    assert new_member.id is not None
    assert len(new_member.id) == 4
    assert new_member.id not in handler.family_tree.members  # Should be unique


def test_create_proto_member_from_dict_valid(proto_handler_empty):
    handler = proto_handler_empty
    new_member_shell = handler.generate_new_member()
    input_data = {
        "name": "Valid User",
        "gender": "FEMALE",
        "IsAlive": True,
        "dob_date": 10,
        "dob_month": 5,
        "dob_year": 1990,
    }
    member_proto, error_msg = handler.create_proto_member_from_dict(
        input_data, new_member_shell
    )
    assert error_msg == ""  # Expect empty string for no error
    assert member_proto is not None
    assert member_proto.name == "Valid User"
    assert member_proto.gender == utils_pb2.FEMALE
    assert member_proto.date_of_birth.year == 1990


def test_create_proto_member_from_dict_invalid_name(proto_handler_empty):
    handler = proto_handler_empty
    new_member_shell = handler.generate_new_member()
    input_data = {"name": "  ", "gender": "MALE"}
    member_proto, error_msg = handler.create_proto_member_from_dict(
        input_data, new_member_shell
    )
    assert member_proto is None
    assert "Validation Error: Name cannot be empty." in error_msg


def test_create_proto_member_from_dict_invalid_date(proto_handler_empty):
    handler = proto_handler_empty
    new_member_shell = handler.generate_new_member()
    input_data = {
        "name": "Bad Date",
        "gender": "OTHER",
        "dob_year": 2000,
        "dob_month": 13,
    }
    member_proto, error_msg = handler.create_proto_member_from_dict(
        input_data, new_member_shell
    )
    assert member_proto is None
    assert (
        "Date of Birth Error: Incomplete Gregorian date" in error_msg
    )  # Or more specific


def test_create_proto_member_from_dict_dod_lt_dob(proto_handler_empty):
    handler = proto_handler_empty
    new_member_shell = handler.generate_new_member()
    input_data = {
        "name": "Time Anomaly",
        "gender": "MALE",
        "IsAlive": False,
        "dob_date": 1,
        "dob_month": 1,
        "dob_year": 2000,
        "dod_date": 1,
        "dod_month": 1,
        "dod_year": 1999,
    }
    member_proto, error_msg = handler.create_proto_member_from_dict(
        input_data, new_member_shell
    )
    assert member_proto is None
    assert "Date of Death cannot be before Date of Birth" in error_msg


def test_prepare_node_attributes_for_member(proto_handler_empty):
    handler = proto_handler_empty
    member = create_simple_member_proto("ATTR1", "Attr Test")
    member.gender = utils_pb2.MALE

    # Mock ResourceUtility.get_default_images
    mock_return_value = ({"MALE": "/path/to/male.png"}, "/path/to/broken.gif")
    # Patching the lookup path in the module where the call is made
    with patch(
        "familytree.proto_handler.ResourceUtility.get_default_images",
        return_value=mock_return_value,
    ) as mock_get_defaults:
        attrs = handler.prepare_node_attributes_for_member(member)
        mock_get_defaults.assert_called_once()

    assert attrs["ID"] == "ATTR1"
    assert attrs["Name"] == "Attr Test"
    assert attrs["NodeImagePath"] == "/path/to/male.png"
    assert attrs["BrokenImage"] == "/path/to/broken.gif"
    assert "Title" in attrs


def test_prepare_node_attributes_custom_image(proto_handler_empty):
    handler = proto_handler_empty
    member = create_simple_member_proto("CUSTIMG", "Custom Image")
    member.additional_info["image_location"] = "/custom/image.jpg"
    mock_default_images_return = (
        {},
        "/path/to/broken.gif",
    )  # No defaults needed if custom exists
    with (
        patch(
            "familytree.proto_handler.ResourceUtility.get_default_images",
            return_value=mock_default_images_return,
        ) as mock_get_defaults,
        patch("os.path.exists", return_value=True, autospec=True) as mock_exists,
    ):
        attrs = handler.prepare_node_attributes_for_member(member)
        mock_exists.assert_called_with("/custom/image.jpg")
        mock_get_defaults.assert_called_once()

    assert attrs["NodeImagePath"] == "/custom/image.jpg"
    assert attrs["BrokenImage"] == "/path/to/broken.gif"


def test_generate_node_title(proto_handler_empty):
    handler = proto_handler_empty
    member = family_tree_pb2.FamilyMember(
        id="TITLE1", name="Title Test", gender=utils_pb2.FEMALE, alive=False
    )
    member.date_of_birth.year = 1980
    member.nicknames.append("TT")
    title = handler.generate_node_title(member)
    assert "Id: TITLE1" in title
    assert "Name: Title Test" in title
    assert "Gender: FEMALE" in title
    assert "Alive: False" in title
    assert "Date Of Birth: {'year': 1980}" in title  # Partial date
    assert "Nicknames: ['TT']" in title


def test_add_member_to_proto_tree(proto_handler_empty):
    handler = proto_handler_empty
    assert len(handler.family_tree.members) == 0
    member = create_simple_member_proto("ADD1", "Added Member")
    handler.add_member_to_proto_tree(member)
    assert len(handler.family_tree.members) == 1
    assert "ADD1" in handler.family_tree.members
    assert handler.family_tree.members["ADD1"].name == "Added Member"

    # Test updating existing member
    updated_member = create_simple_member_proto("ADD1", "Updated Name")
    handler.add_member_to_proto_tree(updated_member)
    assert len(handler.family_tree.members) == 1
    assert handler.family_tree.members["ADD1"].name == "Updated Name"


# --- Relationship and Deletion Tests ---


@pytest.fixture
def proto_handler_for_relations(proto_handler_empty):
    """ProtoHandler with a few members for relationship tests."""
    handler = proto_handler_empty
    handler.add_member_to_proto_tree(create_simple_member_proto("P1", "Parent One"))
    handler.add_member_to_proto_tree(create_simple_member_proto("P2", "Parent Two"))
    handler.add_member_to_proto_tree(create_simple_member_proto("C1", "Child One"))
    return handler


def test_add_relationship_spouse(proto_handler_for_relations):
    handler = proto_handler_for_relations
    # Mock inference to isolate direct addition
    with patch.object(
        handler, "_infer_relations_for_spouse", return_value=[]
    ) as mock_infer:
        established_rels, message = handler.add_relationship("P1", "P2", "spouse")

    assert isinstance(established_rels, list)
    assert ("spouse", "P1", "P2") in established_rels
    assert "Relationships processed." in message  # Default success
    mock_infer.assert_called_once_with(member1_id="P1", member2_id="P2")
    assert "P2" in handler.family_tree.relationships["P1"].spouse_ids
    assert "P1" in handler.family_tree.relationships["P2"].spouse_ids


def test_add_relationship_child(proto_handler_for_relations):
    handler = proto_handler_for_relations
    with patch.object(
        handler, "_infer_relations_for_child", return_value=[]
    ) as mock_infer:
        established_rels, message = handler.add_relationship("P1", "C1", "child")

    assert ("child", "P1", "C1") in established_rels
    mock_infer.assert_called_once_with(member1_id="P1", member2_id="C1")
    assert "C1" in handler.family_tree.relationships["P1"].children_ids
    assert "P1" in handler.family_tree.relationships["C1"].parent_ids


def test_add_relationship_parent(proto_handler_for_relations):
    handler = proto_handler_for_relations
    with patch.object(
        handler, "_infer_relations_for_parent", return_value=[]
    ) as mock_infer:
        established_rels, message = handler.add_relationship(
            "C1", "P2", "parent"
        )  # C1 is child, P2 is parent

    assert ("child", "P2", "C1") in established_rels  # Canonical form
    mock_infer.assert_called_once_with(member1_id="C1", member2_id="P2")
    assert "C1" in handler.family_tree.relationships["P2"].children_ids
    assert "P2" in handler.family_tree.relationships["C1"].parent_ids


def test_delete_member_from_proto_tree_comprehensive(proto_handler_for_relations):
    handler = proto_handler_for_relations
    # Setup: P1 and P2 are spouses. P1 is parent of C1.
    handler.family_tree.relationships["P1"].spouse_ids.append("P2")
    handler.family_tree.relationships["P2"].spouse_ids.append("P1")
    handler.family_tree.relationships["P1"].children_ids.append("C1")
    handler.family_tree.relationships["C1"].parent_ids.append("P1")

    member_to_delete = "P1"
    handler.delete_member_from_proto_tree(member_to_delete)

    assert member_to_delete not in handler.family_tree.members
    assert member_to_delete not in handler.family_tree.relationships
    assert member_to_delete not in handler.family_tree.relationships["P2"].spouse_ids
    assert member_to_delete not in handler.family_tree.relationships["C1"].parent_ids


def test_infer_relations_for_parent_multi_other_parents(proto_handler_empty):
    handler = proto_handler_empty
    # Setup: Child C1 has existing parents P1 and P2. New parent P3 is added.
    handler.add_member_to_proto_tree(create_simple_member_proto("C1", "Child"))
    handler.add_member_to_proto_tree(create_simple_member_proto("P1", "Parent One"))
    handler.add_member_to_proto_tree(create_simple_member_proto("P2", "Parent Two"))
    handler.add_member_to_proto_tree(create_simple_member_proto("P3", "New Parent"))

    handler.family_tree.relationships["C1"].parent_ids.extend(["P1", "P2"])
    handler.family_tree.relationships["P1"].children_ids.append("C1")
    handler.family_tree.relationships["P2"].children_ids.append("C1")

    # Mock _add_spouse_relation and _add_child_relation as they are called by the inference
    with (
        patch.object(
            handler, "_add_spouse_relation", return_value=[]
        ) as mock_add_spouse,
        patch.object(handler, "_add_child_relation", return_value=[]) as mock_add_child,
    ):
        # Action: Add P3 as a parent to C1. This internally calls _infer_relations_for_parent.
        # We are testing _infer_relations_for_parent's logic when called in such a scenario.
        # The direct call to _infer_relations_for_parent is for focused testing.
        inferred_list = handler._infer_relations_for_parent(
            member1_id="C1", member2_id="P3"
        )

    # Assertions for multi-other-parent scenario:
    assert "Child C1 has multiple other parents" in handler.message_to_propagate
    assert (
        "{'P1', 'P2'}" in handler.message_to_propagate
        or "{'P2', 'P1'}" in handler.message_to_propagate
    )
    mock_add_spouse.assert_not_called()  # Spousal relationship is not automatically inferred with all other parents
    # mock_add_child might be called if P1/P2 had other children (step-siblings for C1 via P3)
    # For this specific test setup, P1/P2 have no other children, so mock_add_child shouldn't be called for that reason.
    # If the logic was to make P3 parent of C1's siblings through P1/P2, then it would be called.
    # The current _infer_relations_for_parent focuses on spousal for new parent, and step-parenting to new parent's other children.
    # Let's assume for now no other children of P1/P2 to simplify.
    # If P1/P2 had other children, mock_add_child would be called to make P3 their step-parent.

    # Test updating existing member
    updated_member = create_simple_member_proto("ADD1", "Updated Name")
    handler.add_member_to_proto_tree(updated_member)
    assert len(handler.family_tree.members) == 1
    assert handler.family_tree.members["ADD1"].name == "Updated Name"
