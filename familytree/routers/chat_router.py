import logging

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends

from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.chat_model import ChatRequest, ChatResponse
from familytree.routers import get_current_family_tree_handler_dependency

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/ask", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    family_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Handles the sending of a message, for interacting with an AI assistant related to the family tree.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received query: {request.query}")
    response_text = family_handler.ask_about_family(request.query)

    return ChatResponse(
        status=OK_STATUS,
        message="Response generated successfully",
        response=response_text,
    )
