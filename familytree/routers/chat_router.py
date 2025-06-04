import logging

from fastapi import APIRouter, HTTPException

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
    message = "Endpoint /chat/send_message is not yet implemented."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)
