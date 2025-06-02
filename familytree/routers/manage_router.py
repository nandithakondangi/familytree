import logging

from fastapi import APIRouter, HTTPException
from google.protobuf.json_format import ParseError

from familytree import app_state
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    CreateFamilyResponse,
    LoadFamilyRequest,
    LoadFamilyResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/manage",
    tags=["Manage"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_family", response_model=CreateFamilyResponse)
async def create_new_family():
    """
    Creates a new, empty family tree structure
    """
    try:
        app_state.reset_current_family_tree_handler()
        message = "New family tree created."
        # pyrefly: ignore
        response = CreateFamilyResponse(status=OK_STATUS, message=message)
        return response
    except Exception as e:
        error_message = "Unexpected error occured during create family operation."
        logger.exception(error_message, e)
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/load_family", response_model=LoadFamilyResponse)
async def load_family_data(request: LoadFamilyRequest):
    """
    Loads existing family tree data from a specified source (e.g., a file).
    """
    try:
        app_state.reset_current_family_tree_handler()
        family_handler = app_state.get_current_family_tree_handler()
        return family_handler.load_family_tree(request)
    except Exception:
        error_message = "Unexpected error occured during load family operation."
        logger.exception(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/add_family_member", response_model=AddFamilyMemberResponse)
async def add_family_member(request: AddFamilyMemberRequest):
    """
    Adds a new individual to the currently active family tree.
    """
    try:
        family_handler = app_state.get_current_family_tree_handler()
        return family_handler.add_family_member(request)
    except ParseError:
        error_message = "Failed to parse the new member data."
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    except Exception:
        error_message = "Unexpected error occured during add family member operation"
        logger.exception(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/update_family_member")
async def update_family_member():
    """
    Updates the information of an existing member in the family tree.
    """
    message = "Endpoint /manage/update_family_member is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.post("/delete_family_member")
async def delete_family_member():
    """
    Removes a member from the family tree.
    """
    message = "Endpoint /manage/delete_family_member is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/save_family")
async def save_family_data():
    """
    Saves the current state of the family tree data to a persistent storage.
    """
    message = "Endpoint /manage/save_family_data is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/export_family_snapshot")
async def export_family_snapshot():
    """
    Exports a static snapshot of the current family tree view (e.g., as an image or PDF).
    """
    message = "Endpoint /manage/export_family_snapshot is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/export_interactive_graph")
async def export_interactive_graph():
    """
    Exports the family tree data in a format suitable for an interactive graph visualization.
    """
    message = "Endpoint /manage/export_interactive_graph is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)
