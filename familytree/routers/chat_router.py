import logging

from fastapi import APIRouter

from familytree.exceptions import UnsupportedOperationError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/send_message")
async def send_message():
    """
    Handles the sending of a message, for interacting with an AI assistant related to the family tree.
    """
    raise UnsupportedOperationError(operation="send_message", feature="chatbot")
