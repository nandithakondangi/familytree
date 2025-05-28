import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/manage",
    tags=["Manage"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_family")
async def create_new_family():
    """
    Creates a new, empty family tree structure and adds the first family member.
    """
    message = "Endpoint /manage/create_family is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.post("/load_family")
async def load_family_data():
    """
    Loads existing family tree data from a specified source (e.g., a file).
    """
    message = "Endpoint /manage/load_family_data is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.post("/add_family_member")
async def add_family_member():
    """
    Adds a new individual to the currently active family tree.
    """
    message = "Endpoint /manage/add_family_member is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


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
