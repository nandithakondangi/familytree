import logging

from fastapi import APIRouter
from fastapi.param_functions import Depends

from familytree.exceptions import UnsupportedOperationError
from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.models.graph_model import (
    CustomGraphRenderResponse,
    MemberInfoResponse,
    PyvisGraphRenderResponse,
)
from familytree.routers import get_current_family_tree_handler_dependency

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/graph",
    tags=["Graph"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/render", response_model=PyvisGraphRenderResponse | CustomGraphRenderResponse
)
async def get_data_with_poi(
    theme: str,
    family_tree_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
    poi: str | None = None,
    degree: int = 2,
):
    """
    Renders graph data for the family tree.
    Can be focused on a specific Point of Interest (poi) and show connections
    up to a specified degree of separation.

    Args:
        poi: Optional ID of the person to center the graph on.
        degree: The number of degrees of separation to display from the POI or root.
    """
    if poi:
        raise UnsupportedOperationError(
            operation="render_with_poi", feature=f"poi={poi}, degree={degree}"
        )
    else:
        html_content = family_tree_handler.render_family_tree(theme)
        return PyvisGraphRenderResponse(
            status="OK",  # pyrefly: ignore
            message="Family tree rendered successfully",
            graph_html=html_content,  # pyrefly: ignore
        )


@router.get("/member_info/{user_id}", response_model=MemberInfoResponse)
async def get_member_info(
    user_id: str,
    family_tree_handler: FamilyTreeHandler = Depends(
        get_current_family_tree_handler_dependency
    ),
):
    """
    Retrieves information about a specific member in the family tree.

    Args:
        user_id: The ID of the user whose information is to be retrieved.
    """
    return family_tree_handler.get_member_info(user_id)


@router.get("/expand_parents/{user}")
async def expand_parents(user: str):
    """
    Expands the graph view to display the parents of the specified user.

    Args:
        user: The ID of the user whose parents are to be displayed.
    """
    raise UnsupportedOperationError(
        operation="expand_parents", feature=f"expand_parents for user {user}"
    )


@router.get("/expand_siblings/{user}")
async def expand_siblings(user: str):
    """
    Expands the graph view to display the siblings of the specified user.

    Args:
        user: The ID of the user whose siblings are to be displayed.
    """
    raise UnsupportedOperationError(
        operation="expand_siblings", feature=f"expand_siblings for user {user}"
    )


@router.get("/expand_children/{user}")
async def expand_children(user: str):
    """
    Expands the graph view to display the children of the specified user.

    Args:
        user: The ID of the user whose children are to be displayed.
    """
    raise UnsupportedOperationError(
        operation="expand_children", feature=f"expand_children for user {user}"
    )


@router.get("/expand_spouse/{user}")
async def expand_spouse(user: str):
    """
    Expands the graph view to display the spouse(s) of the specified user.

    Args:
        user: The ID of the user whose spouse(s) are to be displayed.
    """
    raise UnsupportedOperationError(
        operation="expand_spouse", feature=f"expand_spouse for user {user}"
    )


@router.get("/expand_inlaws/{user}")
async def expand_inlaws(user: str):
    """
    Expands the graph view to display the in-laws of the specified user.

    Args:
        user: The ID of the user whose in-laws are to be displayed.
    """
    raise UnsupportedOperationError(
        operation="expand_inlaws", feature=f"expand_inlaws for user {user}"
    )


@router.get("/collapse_parents/{user}")
async def collapse_parents(user: str):
    """
    Collapses the graph view to hide the parents of the specified user.

    Args:
        user: The ID of the user whose parents are to be hidden.
    """
    raise UnsupportedOperationError(
        operation="collapse_parents", feature=f"collapse_parents for user {user}"
    )


@router.get("/collapse_siblings/{user}")
async def collapse_siblings(user: str):
    """
    Collapses the graph view to hide the siblings of the specified user.

    Args:
        user: The ID of the user whose siblings are to be hidden.
    """
    raise UnsupportedOperationError(
        operation="collapse_siblings", feature=f"collapse_siblings for user {user}"
    )


@router.get("/collapse_children/{user}")
async def collapse_children(user: str):
    """
    Collapses the graph view to hide the children of the specified user.

    Args:
        user: The ID of the user whose children are to be hidden.
    """
    raise UnsupportedOperationError(
        operation="collapse_children", feature=f"collapse_children for user {user}"
    )


@router.get("/collapse_spouse/{user}")
async def collapse_spouse(user: str):
    """
    Collapses the graph view to hide the spouse(s) of the specified user.

    Args:
        user: The ID of the user whose spouse(s) are to be hidden.
    """
    raise UnsupportedOperationError(
        operation="collapse_spouse", feature=f"collapse_spouse for user {user}"
    )


@router.get("/collapse_inlaws/{user}")
async def collapse_inlaws(user: str):
    """
    Collapses the graph view to hide the in-laws of the specified user.

    Args:
        user: The ID of the user whose in-laws are to be hidden.
    """
    raise UnsupportedOperationError(
        operation="collapse_inlaws", feature=f"collapse_inlaws for user {user}"
    )
