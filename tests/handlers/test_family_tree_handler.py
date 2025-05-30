from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.handlers.graph_handler import EdgeType, GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import LoadFamilyRequest, LoadFamilyResponse


def test_family_tree_handler_init():
    """
    Tests that FamilyTreeHandler initializes its component handlers.
    """
    handler = FamilyTreeHandler()
    assert isinstance(handler.graph_handler, GraphHandler), (
        "graph_handler should be an instance of GraphHandler"
    )
    assert isinstance(handler.proto_handler, ProtoHandler), (
        "proto_handler should be an instance of ProtoHandler"
    )
    assert isinstance(handler.chat_handler, ChatHandler), (
        "chat_handler should be an instance of ChatHandler"
    )


def test_load_family_tree(
    weasley_family_tree_textproto,  # Fixture from conftest.py
    weasley_family_tree_pb,  # Fixture from conftest.py
):
    """
    Tests the load_family_tree method as an integration test,
    verifying the state of ProtoHandler and GraphHandler.
    """
    handler = FamilyTreeHandler()

    request = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )
    response = handler.load_family_tree(request)

    # Assert response
    assert isinstance(response, LoadFamilyResponse)
    assert response.status == OK_STATUS
    assert response.message == "Family tree loaded successfully."

    weasley_children_ids = [
        "BILLW",
        "CHARW",
        "PERCW",
        "FREDW",
        "GEORW",
        "RONAW",
        "GINNW",
    ]

    assert weasley_family_tree_pb == handler.proto_handler.get_family_tree()

    # Assert GraphHandler state
    graph = handler.graph_handler.get_family_graph()
    assert "ARTHW" in graph.nodes
    assert "MOLLW" in graph.nodes
    for child_id in weasley_children_ids:
        assert child_id in graph.nodes

    assert graph.number_of_nodes() == 9
    assert graph.number_of_edges() == 30

    # Check node data
    arthur_node_data = graph.nodes["ARTHW"]["data"]
    assert isinstance(arthur_node_data, GraphHandler.GraphNode)
    assert arthur_node_data.attributes.name == "Arthur Weasley"
    molly_node_data = graph.nodes["MOLLW"]["data"]
    assert isinstance(molly_node_data, GraphHandler.GraphNode)
    assert molly_node_data.attributes.name == "Molly Weasley"

    assert graph.edges["ARTHW", "MOLLW"]["data"].edge_type == EdgeType.SPOUSE
    assert graph.edges["MOLLW", "ARTHW"]["data"].edge_type == EdgeType.SPOUSE

    for child_id in weasley_children_ids:
        assert graph.edges["ARTHW", child_id]["data"].edge_type == EdgeType.CHILD
        assert graph.edges["ARTHW", child_id]["data"].is_visible
        assert graph.edges[child_id, "ARTHW"]["data"].edge_type == EdgeType.PARENT
        assert not graph.edges[child_id, "ARTHW"]["data"].is_visible
        assert graph.edges["MOLLW", child_id]["data"].edge_type == EdgeType.CHILD
        assert graph.edges[child_id, "MOLLW"]["data"].edge_type == EdgeType.PARENT
