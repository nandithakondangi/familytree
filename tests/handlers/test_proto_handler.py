from unittest.mock import MagicMock, patch

import pytest
from google.protobuf import text_format

from familytree.handlers.proto_handler import ProtoHandler
from familytree.proto import family_tree_pb2, utils_pb2


@pytest.fixture
def proto_handler_instance():
    """Provides an empty ProtoHandler instance for each test."""
    return ProtoHandler()


def test_init(proto_handler_instance):
    """Tests ProtoHandler initialization."""
    assert isinstance(proto_handler_instance._family_tree, family_tree_pb2.FamilyTree)
    assert not proto_handler_instance._family_tree.members


def test_get_family_tree(proto_handler_instance):
    """Tests retrieval of the internal FamilyTree message."""
    assert (
        proto_handler_instance.get_family_tree() is proto_handler_instance._family_tree
    )


def test_load_from_textproto_success(
    proto_handler_instance, weasley_family_tree_textproto
):
    """Tests successful loading from a text protobuf string."""
    proto_handler_instance.load_from_textproto(weasley_family_tree_textproto)
    assert "ARTHW" in proto_handler_instance._family_tree.members
    assert proto_handler_instance._family_tree.members["ARTHW"].name == "Arthur Weasley"


def test_load_from_textproto_parse_error(proto_handler_instance, caplog):
    """Tests loading from a malformed text protobuf string."""
    with pytest.raises(text_format.ParseError):
        proto_handler_instance.load_from_textproto("malformed { proto content")
    assert "Error parsing text proto" in caplog.text


@patch("google.protobuf.text_format.Merge")
def test_load_from_textproto_unexpected_error(
    mock_merge, proto_handler_instance, caplog
):
    """Tests handling of unexpected errors during text proto loading."""
    mock_merge.side_effect = Exception("Unexpected merge failure")
    proto_handler_instance.load_from_textproto("valid content but merge fails")
    # The method catches generic Exception and logs, does not re-raise by default
    assert "An unexpected error occured" in caplog.text


def test_save_to_textproto(proto_handler_instance, weasley_family_tree_textproto):
    """Tests saving the FamilyTree message to a text protobuf string."""
    proto_handler_instance.load_from_textproto(weasley_family_tree_textproto)
    saved_text = proto_handler_instance.save_to_textproto()

    # To verify, parse the saved text back into a new FamilyTree message
    new_tree = family_tree_pb2.FamilyTree()
    text_format.Merge(saved_text, new_tree)
    assert "ARTHW" in new_tree.members
    assert new_tree.members["ARTHW"].name == "Arthur Weasley"
    assert len(new_tree.members) == len(proto_handler_instance._family_tree.members)


def test_create_family_member_minimal():
    """Tests creating a FamilyMember with minimal information."""
    member = ProtoHandler.create_family_member(id_str="M001", name="Minimal Member")
    assert member.id == "M001"
    assert member.name == "Minimal Member"
    assert not member.nicknames
    assert not member.HasField("alive")  # Optional bool not set


def test_create_family_member_all_fields():
    """Tests creating a FamilyMember with all fields populated."""
    dob = utils_pb2.GregorianDate(year=1990, month=1, date=15)
    tdob = utils_pb2.TraditionalDate(month=utils_pb2.CHITHIRAI, star=utils_pb2.ASHWINI)
    dod = utils_pb2.GregorianDate(year=2020, month=5, date=10)
    tdod = utils_pb2.TraditionalDate(month=utils_pb2.AADI, paksham=utils_pb2.KRISHNA)
    wedding_date = utils_pb2.GregorianDate(year=2010, month=6, date=20)

    member = ProtoHandler.create_family_member(
        id_str="M002",
        name="Full Member",
        nicknames=["FM", "Test"],
        date_of_birth=dob,
        traditional_date_of_birth=tdob,
        alive=False,
        date_of_death=dod,
        traditional_date_of_death=tdod,
        gender=utils_pb2.FEMALE,
        birth_family_unit_id=10,
        marriage_family_unit_id=20,
        wedding_date=wedding_date,
        additional_info={"hobby": "testing", "role": "tester"},
    )

    assert member.id == "M002"
    assert member.name == "Full Member"
    assert list(member.nicknames) == ["FM", "Test"]
    assert member.date_of_birth == dob
    assert member.traditional_date_of_birth == tdob
    assert member.alive is False
    assert member.date_of_death == dod
    assert member.traditional_date_of_death == tdod
    assert member.gender == utils_pb2.FEMALE
    assert member.birth_family_unit_id == 10
    assert member.marriage_family_unit_id == 20
    assert member.wedding_date == wedding_date
    assert member.additional_info["hobby"] == "testing"
    assert member.additional_info["role"] == "tester"


@patch.object(ProtoHandler, "update_from_nx_graph")
@patch.object(ProtoHandler, "load_from_textproto")
@patch.object(ProtoHandler, "_deduplicate_family_members")
def test_merge_family_trees(
    mock_deduplicate, mock_load_proto, mock_update_graph, proto_handler_instance
):
    """Tests the merge_family_trees method by checking its calls to dependencies."""
    mock_graph = MagicMock()  # nx.DiGraph()
    other_tree_text = "other tree content"

    proto_handler_instance.merge_family_trees(mock_graph, other_tree_text)

    mock_update_graph.assert_called_once_with(mock_graph)
    mock_load_proto.assert_called_once_with(other_tree_text)
    mock_deduplicate.assert_called_once()


# update_from_nx_graph and _deduplicate_family_members are not implemented,
# so no direct tests for their internal logic.
