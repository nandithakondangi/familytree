import logging

from fastapi import APIRouter, HTTPException

from familytree import app_state
from familytree.models.graph_model import (
    CustomGraphRenderResponse,
    MemberInfoResponse,
    PyvisGraphRenderResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/graph",
    tags=["Graph"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/render", response_model=PyvisGraphRenderResponse | CustomGraphRenderResponse
)
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
            return PyvisGraphRenderResponse(
                status="OK",  # pyrefly: ignore
                message="Family tree rendered successfully",
                graph_html=html_content,  # pyrefly: ignore
            )
        except Exception as e:
            error_message = "Unexpected error occured while rendering family tree"
            logger.exception(f"{error_message}: {e}")
            raise HTTPException(status_code=500, detail=f"{error_message}: {str(e)}")


@router.get("/member_info/{user_id}", response_model=MemberInfoResponse)
async def get_member_info(user_id: str):
    """
    Retrieves information about a specific member in the family tree.

    Args:
        user_id: The ID of the user whose information is to be retrieved.
    """
    try:
        handler = app_state.get_current_family_tree_handler()
        return handler.get_member_info(user_id)
    except Exception as e:
        error_message = "Unexpected error occured while retrieving member info"
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
