import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from familytree.exceptions import UnsupportedOperationError
from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    AddRelationshipRequest,
    AddRelationshipResponse,
    CreateFamilyResponse,
    DeleteFamilyMemberRequest,
    DeleteFamilyMemberResponse,
    DeleteRelationshipRequest,
    DeleteRelationshipResponse,
    ExportInteractiveGraphResponse,
    LoadFamilyRequest,
    LoadFamilyResponse,
    SaveFamilyResponse,
    UpdateFamilyMemberRequest,
    UpdateFamilyMemberResponse,
)
from familytree.routers import (
    get_current_family_tree_handler_dependency,
    get_new_family_tree_handler_dependency,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/manage",
    tags=["Manage"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_family", response_model=CreateFamilyResponse)
async def create_new_family(
    family_tree_handler: FamilyTreeHandler = Depends(
        get_new_family_tree_handler_dependency
    ),
):
    """
    Creates a new, empty family tree structure
    """
    message = "New family tree created."
    # pyrefly: ignore
    return CreateFamilyResponse(status=OK_STATUS, message=message)


@router.post("/load_family", response_model=LoadFamilyResponse)
async def load_family_data(
    request: LoadFamilyRequest,
    family_handler: FamilyTreeHandler = Depends(get_new_family_tree_handler_dependency),
):
    """
    Loads existing family tree data from a specified source (e.g., a file).
    """
    return family_handler.load_family_tree(request)


@router.post("/add_family_member", response_model=AddFamilyMemberResponse)
async def add_family_member(
    request: AddFamilyMemberRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Adds a new individual to the currently active family tree.
    """
    return family_handler.add_family_member(request)


@router.post("/add_relationship", response_model=AddRelationshipResponse)
async def add_relationship(
    request: AddRelationshipRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Adds a relationship between two individuals in the family tree.
    """
    return family_handler.add_relationship(request)


@router.post("/update_family_member", response_model=UpdateFamilyMemberResponse)
async def update_family_member(
    request: UpdateFamilyMemberRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Updates the information of an existing member in the family tree.
    """
    return family_handler.update_family_member(request)


@router.post("/delete_family_member", response_model=DeleteFamilyMemberResponse)
async def delete_family_member(
    request: DeleteFamilyMemberRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Removes a member from the family tree.
    """
    return family_handler.delete_family_member(request)


@router.post("/delete_relationship", response_model=DeleteRelationshipResponse)
async def delete_relationship(
    request: DeleteRelationshipRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Removes a relationship between two individuals from the family tree.
    """
    return family_handler.delete_relationship(request)


@router.get("/save_family", response_model=SaveFamilyResponse)
async def save_family_data(
    visible_only: Annotated[
        bool,
        Query(
            alias="visibleOnly",
            title="Toggle for data to be saved",
            description="Toggles what data to be saved. If true, then currently visible nodes will only be saved, otherwise all nodes will be saved.",
        ),
    ] = False,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Saves the current state of the family tree data to a persistent storage.
    """
    return family_handler.save_family_tree(visible_only)


@router.get("/export_interactive_graph", response_model=ExportInteractiveGraphResponse)
async def export_interactive_graph():
    """
    Exports the family tree data in a format suitable for an interactive graph visualization.
    """
    raise UnsupportedOperationError(
        operation="export_interactive_graph", feature="export_interactive_graph"
    )
