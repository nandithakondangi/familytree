from typing import Any, Optional

from familytree.models.base_model import FamilyTreeBaseResponse


class PyvisGraphRenderResponse(FamilyTreeBaseResponse):
    graph_html: Optional[str] = None


class CustomGraphRenderResponse(FamilyTreeBaseResponse):
    pass


class MemberInfoResponse(FamilyTreeBaseResponse):
    member_info: Optional[dict[str, Any]] = None
