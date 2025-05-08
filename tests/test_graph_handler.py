import os
from unittest.mock import patch

import pytest

from familytree.graph_handler import COLOR_PALETTLE, GraphHandler


@pytest.fixture
def graph_handler_empty(tmp_path):
    """Provides an empty GraphHandler instance."""
    output_html = tmp_path / "test_graph.html"
    return GraphHandler(output_html_file=str(output_html))


@pytest.fixture
def graph_handler_with_nodes(graph_handler_empty):
    """Provides a GraphHandler with a few nodes and edges."""
    handler = graph_handler_empty
    handler.add_node_in_graph(
        "P1", "Parent One", "P1 Title", "/img/p1.png", "/img/broken.png"
    )
    handler.add_node_in_graph(
        "P2", "Parent Two", "P2 Title", "/img/p2.png", "/img/broken.png"
    )
    handler.add_node_in_graph(
        "C1", "Child One", "C1 Title", None, "/img/broken.png"
    )  # No image

    handler.add_spouse_edges("P1", "P2")
    handler.add_child_edges("P1", "C1")
    handler.add_child_edges("P2", "C1")
    return handler


# --- GraphHandler Tests ---


def test_add_node_in_graph(graph_handler_empty):
    handler = graph_handler_empty
    handler.add_node_in_graph(
        member_id="N1",
        member_name="Node One",
        title_str="Tooltip for N1",
        final_image_path="/path/image.png",
        brokenImage="/path/broken.gif",
    )
    assert "N1" in handler.nx_graph.nodes
    node_data = handler.nx_graph.nodes["N1"]
    assert node_data["label"] == "Node One"
    assert node_data["title"] == "Tooltip for N1"
    assert node_data["shape"] == "circularImage"
    assert node_data["image"] == "/path/image.png"
    assert node_data["brokenImage"] == "/path/broken.gif"

    # Test updating a node
    handler.add_node_in_graph(
        member_id="N1",
        member_name="Node One Updated",
        title_str="New Tooltip",
        final_image_path=None,  # Remove image
        brokenImage="/path/broken.gif",
    )
    node_data_updated = handler.nx_graph.nodes["N1"]
    assert node_data_updated["label"] == "Node One Updated"
    assert node_data_updated["title"] == "New Tooltip"
    assert node_data_updated["shape"] == "dot"  # Shape changes if no image
    assert node_data_updated["image"] is None


def test_add_spouse_edges(graph_handler_empty):
    handler = graph_handler_empty
    handler.add_node_in_graph("S1", "Spouse 1", "", None, "")
    handler.add_node_in_graph("S2", "Spouse 2", "", None, "")
    handler.add_spouse_edges("S1", "S2")

    assert handler.nx_graph.has_edge("S1", "S2")
    assert handler.nx_graph.edges["S1", "S2"]["color"] == COLOR_PALETTLE["pink"]
    assert handler.nx_graph.edges["S1", "S2"]["weight"] == 0
    assert handler.nx_graph.has_edge("S2", "S1")  # Bidirectional for spouse
    assert handler.nx_graph.edges["S2", "S1"]["color"] == COLOR_PALETTLE["pink"]
    assert handler.nx_graph.edges["S2", "S1"]["weight"] == 0


def test_add_child_edges(graph_handler_empty):
    handler = graph_handler_empty
    handler.add_node_in_graph("P1", "Parent", "", None, "")
    handler.add_node_in_graph("C1", "Child", "", None, "")
    handler.add_child_edges("P1", "C1")

    assert handler.nx_graph.has_edge("P1", "C1")  # Visible parent->child
    assert handler.nx_graph.edges["P1", "C1"]["weight"] == 1
    assert handler.nx_graph.has_edge("C1", "P1")  # Hidden child->parent
    assert handler.nx_graph.edges["C1", "P1"]["weight"] == -1


def test_display_family_tree_success(graph_handler_with_nodes):
    handler = graph_handler_with_nodes
    handler.display_family_tree()
    assert os.path.exists(handler.output_html_file)
    assert os.path.getsize(handler.output_html_file) > 500  # Basic check for content


def test_display_family_tree_empty_graph(graph_handler_empty):
    handler = graph_handler_empty
    handler.display_family_tree()  # Should create an empty placeholder HTML
    assert os.path.exists(handler.output_html_file)
    with open(handler.output_html_file, "r") as f:
        content = f.read()
        assert (
            "No family tree data loaded." in content
            or "Graph contains only hidden edges" in content
        )


@patch("os.makedirs")
def test_display_family_tree_dir_error(mock_makedirs, tmp_path):
    mock_makedirs.side_effect = OSError("Permission denied for test")
    # Create a path that would require a new directory
    uncreatable_output_file = tmp_path / "new_dir" / "test.html"
    handler = GraphHandler(output_html_file=str(uncreatable_output_file))
    # Add a node to avoid the "empty graph" path
    handler.add_node_in_graph("N1", "Node", "", None, "")

    with pytest.raises(IOError) as excinfo:
        handler.display_family_tree()
    assert "Cannot create output directory" in str(excinfo.value)
    assert "Permission denied for test" in str(excinfo.value.__cause__)


def test_filter_graph_by_weight(graph_handler_with_nodes):
    handler = graph_handler_with_nodes
    original_graph = handler.nx_graph
    # P1-P2 (spouse, weight 0, both ways = 2 edges)
    # P1-C1 (child, weight 1) + C1-P1 (hidden, weight -1) = 2 edges
    # P2-C1 (child, weight 1) + C1-P2 (hidden, weight -1) = 2 edges
    # Total = 6 edges
    assert original_graph.number_of_edges() == 6

    filtered_graph = handler._filter_graph_by_weight(
        weight_to_filter_out=-1
    )  # Filter hidden
    # Expected: 2 spouse + 2 parent->child = 4 edges
    assert filtered_graph.number_of_edges() == 4
    assert not filtered_graph.has_edge("C1", "P1")
    assert not filtered_graph.has_edge("C1", "P2")
    assert filtered_graph.has_edge("P1", "C1")


def test_get_graph_summary_text(graph_handler_with_nodes):
    handler = graph_handler_with_nodes
    summary = handler.get_graph_summary_text()
    assert "Family Tree Summary:" in summary
    assert "Parent One (ID: P1)" in summary
    assert "Child One (ID: C1)" in summary
    assert "married to Parent Two whose ID is P2" in summary  # Check relationship text
    assert "has child Child One whose ID is C1" in summary


def test_get_graph_summary_text_empty(graph_handler_empty):
    handler = graph_handler_empty
    summary = handler.get_graph_summary_text()
    assert "The family tree data is not loaded or is empty." in summary
