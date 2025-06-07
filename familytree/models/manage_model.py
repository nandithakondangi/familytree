from typing import Any, Optional

from pydantic import BaseModel, field_serializer

from familytree.handlers.graph_handler import EdgeType
from familytree.models.base_model import FamilyTreeBaseResponse


class CreateFamilyResponse(FamilyTreeBaseResponse):
    pass


class LoadFamilyRequest(BaseModel):
    filename: str
    content: str


class LoadFamilyResponse(FamilyTreeBaseResponse):
    pass


class AddFamilyMemberRequest(BaseModel):
    infer_relationships: bool
    new_member_data: dict[str, Any]  # Dictionary representing FamilyMember proto
    source_family_member_id: Optional[str] = None
    relationship_type: Optional[EdgeType] = None

    @field_serializer("relationship_type")
    def serialize_relationship_type(self, v: Optional[EdgeType]):
        if v is None:
            return None
        return v.value  # pragma: no cover


class AddFamilyMemberResponse(FamilyTreeBaseResponse):
    pass
