import logging
import re

from familytree import app_state
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddRelationshipRequest,
    DeleteFamilyMemberRequest,
    DeleteRelationshipRequest,
    LoadFamilyRequest,
    UpdateFamilyMemberRequest,
)
from familytree.utils.graph_types import EdgeType

MEMBER_ID_PATTERN = r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$"
logger = logging.getLogger(__name__)


def test_create_new_family_success(client, reset_app_state_between_tests):
    """Tests successful creation of a new family tree."""
    response = client.post("/api/v1/manage/create_family")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "New family tree created."


def test_load_family_data_success(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """Tests successful loading of family data."""
    request_data = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )

    response = client.post("/api/v1/manage/load_family", json=request_data.model_dump())

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "Family tree loaded successfully."


def test_load_family_data_invalid_input(client, reset_app_state_between_tests):
    """Tests handling of invalid input when loading family data.

    Verifies that a malformed text proto content results in a 400 Bad Request."""
    request_data = LoadFamilyRequest(
        filename="invalid.textpb", content="invalid content"
    )

    response = client.post("/api/v1/manage/load_family", json=request_data.model_dump())

    assert response.status_code == 400
    assert response.json()["status"] == "ERROR"
    assert "Failed to parse request data" in response.json()["message"]


def test_add_first_family_member_e2e(client, reset_app_state_between_tests):
    """E2E test for adding the very first family member to a new tree."""
    new_member_name = "Adam"
    request_payload = AddFamilyMemberRequest(
        new_member_data={
            "name": new_member_name,
        },
        source_family_member_id=None,
        relationship_type=None,
        infer_relationships=False,
    )

    response = client.post(
        "/api/v1/manage/add_family_member",
        json=request_payload.model_dump(exclude_none=True),
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert (
        json_response["message"]
        == f"{new_member_name} added successfully to the family."
    )
    assert re.match(MEMBER_ID_PATTERN, json_response["new_member_id"])


def test_add_family_member_with_relationship_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for adding a second family member to an existing tree."""
    # setup
    request_data = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )
    response = client.post("/api/v1/manage/load_family", json=request_data.model_dump())
    assert response.status_code == 200
    family_handler = app_state.get_current_family_tree_handler()

    # add member without infer relationships
    new_member_name = "Harry"
    request_payload = AddFamilyMemberRequest(
        new_member_data={
            "name": new_member_name,
        },
        source_family_member_id="GINNW",
        relationship_type=EdgeType.SPOUSE,
        infer_relationships=False,
    )

    response = client.post(
        "/api/v1/manage/add_family_member", json=request_payload.model_dump()
    )
    assert response.status_code == 200
    assert response.json()["status"] == OK_STATUS
    assert (
        response.json()["message"]
        == f"{new_member_name} added successfully to the family."
    )
    assert re.match(MEMBER_ID_PATTERN, response.json()["new_member_id"])
    harry_id = response.json()["new_member_id"]
    assert family_handler.graph_handler.get_spouse("GINNW") == harry_id

    # add member with infer relationship
    new_member_name = "Albus Severus"
    request_payload = AddFamilyMemberRequest(
        new_member_data={
            "name": new_member_name,
        },
        source_family_member_id="GINNW",
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=True,
    )

    response = client.post(
        "/api/v1/manage/add_family_member", json=request_payload.model_dump()
    )
    assert response.status_code == 200
    assert response.json()["status"] == OK_STATUS
    assert (
        response.json()["message"]
        == f"{new_member_name} added successfully to the family."
    )
    assert (
        family_handler.graph_handler.get_children("GINNW")[0]
        == response.json()["new_member_id"]
    )
    assert (
        family_handler.graph_handler.get_children(harry_id)[0]
        == response.json()["new_member_id"]
    )


def test_add_relationship_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for adding a relationship between two existing members."""
    # 1. Setup: Load existing family and add a new member to connect to.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200

    fleur_payload = AddFamilyMemberRequest(
        new_member_data={"name": "Fleur Delacour"}, infer_relationships=False
    )
    fleur_response = client.post(
        "/api/v1/manage/add_family_member",
        json=fleur_payload.model_dump(exclude_none=True),
    )
    assert fleur_response.status_code == 200
    fleur_id = fleur_response.json()["new_member_id"]

    # 2. Test case: Add relationship WITH inverse
    add_rel_payload_inverse = AddRelationshipRequest(
        source_member_id="BILLW",  # Bill Weasley
        target_member_id=fleur_id,
        relationship_type=EdgeType.SPOUSE,
        add_inverse_relationship=True,
    )

    response_inverse = client.post(
        "/api/v1/manage/add_relationship", json=add_rel_payload_inverse.model_dump()
    )

    assert response_inverse.status_code == 200
    json_response_inverse = response_inverse.json()
    assert json_response_inverse["status"] == OK_STATUS
    assert "Relationship between BILLW and" in json_response_inverse["message"]

    family_handler = app_state.get_current_family_tree_handler()
    graph = family_handler.graph_handler.get_family_graph()

    assert graph.has_edge("BILLW", fleur_id)
    assert graph.has_edge(fleur_id, "BILLW")

    # 3. Test case: Add relationship WITHOUT inverse
    add_rel_payload_no_inverse = AddRelationshipRequest(
        source_member_id="MOLLW",
        target_member_id=fleur_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,
        add_inverse_relationship=False,
    )

    response_no_inverse = client.post(
        "/api/v1/manage/add_relationship", json=add_rel_payload_no_inverse.model_dump()
    )

    assert response_no_inverse.status_code == 200
    json_response_no_inverse = response_no_inverse.json()
    assert json_response_no_inverse["status"] == OK_STATUS
    assert "Relationship between MOLLW and" in json_response_no_inverse["message"]

    graph = family_handler.graph_handler.get_family_graph()
    assert graph.has_edge("MOLLW", fleur_id)
    assert not graph.has_edge(fleur_id, "MOLLW")


def test_update_family_member_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for updating an existing family member's details."""
    # 1. Setup: Load the Weasley family tree.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200

    # 2. Define the update payload. Let's change Arthur's name and alive status.
    member_id_to_update = "ARTHW"
    updated_data = {
        "name": "Arthur 'Wizard' Weasley",
        "alive": False,
    }
    update_payload = UpdateFamilyMemberRequest(
        member_id=member_id_to_update,
        updated_member_data=updated_data,
    )

    # 3. Send the update request.
    response = client.post(
        "/api/v1/manage/update_family_member",
        json=update_payload.model_dump(),
    )

    # 4. Assert the response is successful.
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert (
        json_response["message"]
        == f"Member {member_id_to_update} updated successfully."
    )

    # 5. Verify the update by checking the member's info.
    family_handler = app_state.get_current_family_tree_handler()
    member_info = family_handler.graph_handler.get_member_info(member_id_to_update)

    assert member_info["name"] == updated_data["name"]
    assert not member_info["alive"]
    # Verify other data is preserved
    assert member_info["id"] == "ARTHW"
    assert member_info["gender"] == "MALE"


def test_update_family_member_not_found(client, reset_app_state_between_tests):
    """Tests updating a family member who does not exist returns a 404."""
    update_payload = UpdateFamilyMemberRequest(
        member_id="XXXX", updated_member_data={"name": "No One"}
    )
    response = client.post(
        "/api/v1/manage/update_family_member", json=update_payload.model_dump()
    )

    assert response.status_code == 404
    json_response = response.json()
    assert json_response["status"] == "ERROR"
    assert "Member with ID 'XXXX' not found" in json_response["message"]


def test_delete_family_member_without_orphans_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for deleting a member without removing their neighbors."""
    # 1. Setup: Load the family tree.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    client.post("/api/v1/manage/load_family", json=load_request.model_dump())

    # 2. Define the delete payload.
    member_id_to_delete = "PERCW"  # Percy Weasley
    delete_payload = DeleteFamilyMemberRequest(
        member_id=member_id_to_delete, remove_orphaned_neighbors=False
    )

    # 3. Send the delete request.
    response = client.post(
        "/api/v1/manage/delete_family_member", json=delete_payload.model_dump()
    )

    # 4. Assert the response is successful.
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "Member deleted successfully."

    # 5. Verify the member is deleted but neighbors are not.
    family_handler = app_state.get_current_family_tree_handler()
    graph = family_handler.graph_handler.get_family_graph()

    assert not graph.has_node(member_id_to_delete)
    assert graph.has_node("ARTHW")  # Percy's parent
    assert graph.has_node("BILLW")  # Percy's sibling


def test_delete_family_member_with_orphans_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for deleting a member and removing their orphaned neighbor."""
    # 1. Setup: Load family and add a new member who will be orphaned.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    client.post("/api/v1/manage/load_family", json=load_request.model_dump())

    # Add Audrey, Percy's spouse, who is only connected to Percy.
    audrey_payload = AddFamilyMemberRequest(
        new_member_data={"name": "Audrey"},
        source_family_member_id="PERCW",
        relationship_type=EdgeType.SPOUSE,
        infer_relationships=False,
    )
    audrey_response = client.post(
        "/api/v1/manage/add_family_member", json=audrey_payload.model_dump()
    )
    audrey_id = audrey_response.json()["new_member_id"]

    family_handler = app_state.get_current_family_tree_handler()
    graph = family_handler.graph_handler.get_family_graph()
    family_units_before = family_handler.graph_handler.get_family_unit_graph()
    assert graph.has_node("PERCW") and graph.has_node(audrey_id)
    assert len(family_units_before) == 2

    # 2. Delete Percy and remove orphans.
    delete_payload = DeleteFamilyMemberRequest(
        member_id="PERCW", remove_orphaned_neighbors=True
    )
    response = client.post(
        "/api/v1/manage/delete_family_member", json=delete_payload.model_dump()
    )

    # 3. Assert success and verify both members are gone.
    assert response.status_code == 200
    assert response.json()["status"] == OK_STATUS

    graph_after = family_handler.graph_handler.get_family_graph()
    family_units_after = family_handler.graph_handler.get_family_unit_graph()
    assert not graph_after.has_node("PERCW")
    assert not graph_after.has_node(audrey_id)  # Audrey should be removed
    assert len(family_units_after) == 1


def test_delete_family_member_not_found(client, reset_app_state_between_tests):
    """Tests deleting a family member who does not exist returns a 404."""
    delete_payload = DeleteFamilyMemberRequest(member_id="XXXX")
    response = client.post(
        "/api/v1/manage/delete_family_member", json=delete_payload.model_dump()
    )

    assert response.status_code == 404
    json_response = response.json()
    assert json_response["status"] == "ERROR"
    assert "Member with ID 'XXXX' not found" in json_response["message"]


def test_delete_relationship_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for deleting a relationship between two members."""
    # 1. Setup: Load the family tree.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    client.post("/api/v1/manage/load_family", json=load_request.model_dump())
    family_handler = app_state.get_current_family_tree_handler()
    graph = family_handler.graph_handler.get_family_graph()

    # Verify initial state: Arthur and Molly are spouses.
    assert graph.has_edge("ARTHW", "MOLLW")
    assert graph.has_edge("MOLLW", "ARTHW")

    # 2. Test case: Delete relationship WITHOUT inverse.
    delete_payload_no_inverse = DeleteRelationshipRequest(
        source_member_id="ARTHW",
        target_member_id="MOLLW",
        remove_inverse_relationship=False,
    )
    response_no_inverse = client.post(
        "/api/v1/manage/delete_relationship",
        json=delete_payload_no_inverse.model_dump(),
    )

    assert response_no_inverse.status_code == 200
    assert response_no_inverse.json()["status"] == OK_STATUS
    assert response_no_inverse.json()["message"] == "Relationship deleted successfully."

    # Verify graph state after deletion without inverse.
    assert not graph.has_edge("ARTHW", "MOLLW")
    assert graph.has_edge("MOLLW", "ARTHW")  # Inverse should still exist.

    # 3. Test case: Delete relationship WITH inverse.
    # Verify initial state for Percy and Arthur.
    assert graph.has_edge("PERCW", "ARTHW")  # child-to-parent
    assert graph.has_edge("ARTHW", "PERCW")  # parent-to-child

    delete_payload_with_inverse = DeleteRelationshipRequest(
        source_member_id="PERCW",
        target_member_id="ARTHW",
        remove_inverse_relationship=True,
    )
    response_with_inverse = client.post(
        "/api/v1/manage/delete_relationship",
        json=delete_payload_with_inverse.model_dump(),
    )

    assert response_with_inverse.status_code == 200
    assert response_with_inverse.json()["status"] == OK_STATUS

    # Verify graph state after deletion with inverse.
    assert not graph.has_edge("PERCW", "ARTHW")
    assert not graph.has_edge("ARTHW", "PERCW")


def test_delete_relationship_not_found(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """Tests deleting a relationship that does not exist returns a 400."""
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    client.post("/api/v1/manage/load_family", json=load_request.model_dump())

    delete_payload = DeleteRelationshipRequest(
        source_member_id="GINNW", target_member_id="CHARW"
    )
    response = client.post(
        "/api/v1/manage/delete_relationship", json=delete_payload.model_dump()
    )

    assert response.status_code == 400
    json_response = response.json()
    assert json_response["status"] == "ERROR"
    assert "Relationship between GINNW and CHARW not found" in json_response["message"]


def test_save_family_data_e2e(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """E2E test for saving the current family tree data."""
    # 1. Setup: Load the Weasley family tree.
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200

    # 2. Call the save endpoint.
    response = client.get("/api/v1/manage/save_family")

    # 3. Assert the response is successful.
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "Created family tree text proto"
    saved_textproto = json_response["family_tree_txtpb"]
    assert isinstance(saved_textproto, str)
    assert len(saved_textproto) > 0

    # 4. Verify the content of the saved data.
    assert saved_textproto == weasley_family_tree_textproto


def test_export_interactive_graph_not_implemented(client):
    """Tests that the /manage/export_interactive_graph endpoint returns 501 Not Implemented."""
    response = client.get("/api/v1/manage/export_interactive_graph")
    json_response = response.json()
    assert response.status_code == 501
    assert json_response["status"] == "ERROR"
    assert (
        json_response["message"]
        == "Unsupported operation 'export_interactive_graph'. Feature 'export_interactive_graph' is not implemented."
    )
