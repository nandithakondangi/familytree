import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from familytree import app_state

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/graph",
    tags=["Graph"],
    responses={404: {"description": "Not found"}},
)


@router.get("/render")
async def get_data_with_poi(poi: str | None = None, degree: int = 2):
    """
    Renders graph data for the family tree.
    Can be focused on a specific Point of Interest (poi) and show connections
    up to a specified degree of separation.

    Args:
        poi: Optional ID of the person to center the graph on.
        degree: The number of degrees of separation to display from the POI or root.
    """
    if poi:
        message = (
            f"Endpoint /graph/render?poi={poi}&degree={degree} is not implemented yet."
        )
        logger.warning(message)
        raise HTTPException(status_code=501, detail=message)
    else:
        try:
            handler = app_state.get_current_family_tree_handler()
            html_content = handler.render_family_tree()
            return HTMLResponse(content=html_content, status_code=200)
        except Exception as e:
            error_message = "Unexpected error occured while rendering family tree"
            logger.exception(f"{error_message}: {e}")
            raise HTTPException(status_code=500, detail=f"{error_message}: {str(e)}")


@router.get("/expand_parents/{user}")
async def expand_parents(user: str):
    """
    Expands the graph view to display the parents of the specified user.

    Args:
        user: The ID of the user whose parents are to be displayed.
    """
    message = f"Endpoint /graph/expand_parents/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/expand_siblings/{user}")
async def expand_siblings(user: str):
    """
    Expands the graph view to display the siblings of the specified user.

    Args:
        user: The ID of the user whose siblings are to be displayed.
    """
    message = f"Endpoint /graph/expand_siblings/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/expand_children/{user}")
async def expand_children(user: str):
    """
    Expands the graph view to display the children of the specified user.

    Args:
        user: The ID of the user whose children are to be displayed.
    """
    message = f"Endpoint /graph/expand_children/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/expand_spouse/{user}")
async def expand_spouse(user: str):
    """
    Expands the graph view to display the spouse(s) of the specified user.

    Args:
        user: The ID of the user whose spouse(s) are to be displayed.
    """
    message = f"Endpoint /graph/expand_spouse/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/expand_inlaws/{user}")
async def expand_inlaws(user: str):
    """
    Expands the graph view to display the in-laws of the specified user.

    Args:
        user: The ID of the user whose in-laws are to be displayed.
    """
    message = f"Endpoint /graph/expand_inlaws/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/collapse_parents/{user}")
async def collapse_parents(user: str):
    """
    Collapses the graph view to hide the parents of the specified user.

    Args:
        user: The ID of the user whose parents are to be hidden.
    """
    message = f"Endpoint /graph/collapse_parents/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/collapse_siblings/{user}")
async def collapse_siblings(user: str):
    """
    Collapses the graph view to hide the siblings of the specified user.

    Args:
        user: The ID of the user whose siblings are to be hidden.
    """
    message = f"Endpoint /graph/collapse_siblings/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/collapse_children/{user}")
async def collapse_children(user: str):
    """
    Collapses the graph view to hide the children of the specified user.

    Args:
        user: The ID of the user whose children are to be hidden.
    """
    message = f"Endpoint /graph/collapse_children/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/collapse_spouse/{user}")
async def collapse_spouse(user: str):
    """
    Collapses the graph view to hide the spouse(s) of the specified user.

    Args:
        user: The ID of the user whose spouse(s) are to be hidden.
    """
    message = f"Endpoint /graph/collapse_spouse/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)


@router.get("/collapse_inlaws/{user}")
async def collapse_inlaws(user: str):
    """
    Collapses the graph view to hide the in-laws of the specified user.

    Args:
        user: The ID of the user whose in-laws are to be hidden.
    """
    message = f"Endpoint /graph/collapse_inlaws/{user} is not implemented yet."
    logger.warning(message)
    raise HTTPException(status_code=501, detail=message)
